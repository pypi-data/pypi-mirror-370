import asyncio
import os
import re
import time
import shutil
import yaml
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import aiofiles
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm
from rich.logging import RichHandler

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.callbacks.base import BaseCallbackHandler


@dataclass
class TranslationConfig:
    source_dir: Path
    output_dir: Path
    model_provider: str
    model_name: str
    api_key: str
    base_url: Optional[str] = None
    max_concurrent: int = 3
    rate_limit_delay: float = 0.8
    chunk_size: int = 2000
    source_lang: str = "English"
    target_lang: str = "Chinese"
    preserve_formatting: bool = True
    auto_confirm: bool = False
    copy_assets: bool = True
    skip_unchanged: bool = True  # 输出文件较新时跳过


class RateLimiter:
    """RPM + 全局退避"""
    def __init__(self, max_requests_per_minute: int = 50):
        self.max_requests_per_minute = max_requests_per_minute
        self.requests: List[float] = []
        self.lock = asyncio.Lock()
        self.backoff_until: float = 0.0

    async def acquire(self):
        while True:
            wait_for = 0.0
            async with self.lock:
                now = time.time()
                if now < self.backoff_until:
                    wait_for = max(wait_for, self.backoff_until - now)

                self.requests = [t for t in self.requests if now - t < 60]
                if wait_for == 0.0 and len(self.requests) >= self.max_requests_per_minute:
                    oldest = min(self.requests) if self.requests else now
                    rpm_wait = 60 - (now - oldest)
                    if rpm_wait > 0:
                        wait_for = max(wait_for, rpm_wait)

                if wait_for == 0.0:
                    self.requests.append(now)
                    return
            await asyncio.sleep(wait_for + 0.01)

    async def trigger_backoff(self, seconds: float):
        async with self.lock:
            until = time.time() + seconds
            if until > self.backoff_until:
                self.backoff_until = until


class ProgressCallbackHandler(BaseCallbackHandler):
    def __init__(self, progress: Progress, task_id):
        self.progress = progress
        self.task_id = task_id

    def on_llm_start(self, serialized, prompts, **kwargs):
        self.progress.update(self.task_id, description="🤖 正在调用AI模型...")

    def on_llm_end(self, response, **kwargs):
        self.progress.update(self.task_id, description="✅ AI响应完成")


class MarkdownTranslator:
    def __init__(self, config: TranslationConfig):
        self.config = config
        self.console = Console()
        self.rate_limiter = RateLimiter(max_requests_per_minute=50)
        self.llm = self._setup_llm()
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True)]
        )
        self.logger = logging.getLogger("translator")

    def _setup_llm(self):
        """懒加载模型依赖，按 provider 提示安装 extras"""
        provider = self.config.model_provider.lower()
        if provider == "openai":
            try:
                from langchain_openai import ChatOpenAI
            except ImportError as e:
                raise RuntimeError(
                    "检测到 provider=openai，但未安装可选依赖。\n"
                    "请先安装: pip install mdtranslator[openai]"
                ) from e
            return ChatOpenAI(
                model=self.config.model_name,
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                temperature=0.1,
                max_retries=3
            )
        elif provider == "anthropic":
            try:
                from langchain_anthropic import ChatAnthropic
            except ImportError as e:
                raise RuntimeError(
                    "检测到 provider=anthropic，但未安装可选依赖。\n"
                    "请先安装: pip install mdtranslator[anthropic]"
                ) from e
            return ChatAnthropic(
                model=self.config.model_name,
                api_key=self.config.api_key,
                temperature=0.1,
                max_retries=3
            )
        elif provider == "google":
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
            except ImportError as e:
                raise RuntimeError(
                    "检测到 provider=google，但未安装可选依赖。\n"
                    "请先安装: pip install mdtranslator[google]"
                ) from e
            return ChatGoogleGenerativeAI(
                model=self.config.model_name,
                google_api_key=self.config.api_key,
                temperature=0.1,
                max_retries=3
            )
        else:
            raise ValueError(f"不支持的模型提供商: {provider}")

    def _extract_markdown_blocks(self, content: str) -> List[Tuple[str, str]]:
        """提取Markdown内容块，区分代码块和普通文本"""
        blocks = []
        lines = content.split('\n')
        current_block = []
        current_type = 'text'
        in_code_block = False
        code_fence_pattern = re.compile(r'^```')

        for line in lines:
            if code_fence_pattern.match(line):
                if in_code_block:
                    current_block.append(line)
                    blocks.append(('code', '\n'.join(current_block)))
                    current_block = []
                    current_type = 'text'
                    in_code_block = False
                else:
                    if current_block:
                        blocks.append((current_type, '\n'.join(current_block)))
                        current_block = []
                    current_block.append(line)
                    current_type = 'code'
                    in_code_block = True
            else:
                current_block.append(line)

        if current_block:
            blocks.append((current_type, '\n'.join(current_block)))

        return blocks

    def _create_translation_prompt(self, text: str) -> str:
        return f"""你是一个专业的技术文档翻译专家。请将以下{self.config.source_lang}文本翻译成{self.config.target_lang}。

翻译要求：
1. 保持原文的格式和结构
2. 准确翻译技术术语
3. 保持Markdown语法不变
4. 翻译要自然流畅，符合中文表达习惯
5. 对于专业术语，在首次出现时可以保留英文原文（中文翻译）的形式
6. 不要添加任何解释或注释，只返回翻译结果

原文：
{text}

翻译："""

    def _is_rate_limit_error(self, e: Exception) -> bool:
        code = getattr(e, "status_code", None) or getattr(e, "code", None)
        if isinstance(code, int) and code == 429:
            return True
        resp = getattr(e, "response", None)
        try:
            if resp is not None:
                sc = getattr(resp, "status_code", None) or getattr(resp, "status", None)
                if isinstance(sc, int) and sc == 429:
                    return True
        except Exception:
            pass
        name = e.__class__.__name__.lower()
        msg = (str(e) or repr(e)).lower()
        keywords = [
            "429", "too many requests", "rate limit", "ratelimit",
            "resource exhausted", "quota exceeded", "exceeded your current quota"
        ]
        if any(k in name for k in ["ratelimit", "rate_limit", "throttl"]):
            return True
        return any(k in msg for k in keywords)

    async def _translate_text_chunk(self, chunk: str, progress: Progress, task_id) -> str:
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            await self.rate_limiter.acquire()
            try:
                callback_handler = ProgressCallbackHandler(progress, task_id)
                messages = [
                    SystemMessage(content="你是一个专业的技术文档翻译专家。"),
                    HumanMessage(content=self._create_translation_prompt(chunk))
                ]
                response = await self.llm.ainvoke(
                    messages,
                    config={"callbacks": [callback_handler]}
                )
                return response.content.strip()
            except Exception as e:
                if self._is_rate_limit_error(e):
                    progress.update(task_id, description="⏸️ 触发限流(429)，暂停10分钟后重试...")
                    self.logger.warning("⚠️ 检测到 429/限流：暂停 10 分钟后重试（第 %d/%d 次）", attempt, max_attempts)
                    await self.rate_limiter.trigger_backoff(600)
                    if attempt == max_attempts:
                        self.logger.error("多次限流后仍失败，保留原文。")
                        return chunk
                    continue
                self.logger.exception("翻译失败（非限流错误）")
                return chunk
        return chunk

    def _should_skip(self, src: Path, dst: Path) -> bool:
        if not self.config.skip_unchanged:
            return False
        if not dst.exists():
            return False
        try:
            return dst.stat().st_mtime >= src.stat().st_mtime
        except Exception:
            return False

    async def _translate_file(self, file_path: Path) -> bool:
        try:
            relative_path = file_path.relative_to(self.config.source_dir)
            output_path = self.config.output_dir / relative_path

            if self._should_skip(file_path, output_path):
                self.logger.info(f"⏭️ 跳过（未变化）: {relative_path}")
                return True

            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()

            translated_content = await self._translate_content(content, relative_path.as_posix())

            output_path.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
                await f.write(translated_content)

            self.logger.info(f"✅ 完成: {relative_path}")
            return True

        except Exception as e:
            self.logger.error(f"❌ 翻译文件失败 {file_path}: {e}")
            return False

    async def _translate_content(self, content: str, filename: str) -> str:
        blocks = self._extract_markdown_blocks(content)
        translated_blocks = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console,
            expand=True
        ) as progress:
            task = progress.add_task(f"翻译 {filename}", total=len(blocks))

            for i, (block_type, block_content) in enumerate(blocks):
                if block_type == 'code':
                    translated_blocks.append(block_content)
                    progress.update(task, description=f"跳过代码块 ({i+1}/{len(blocks)})")
                else:
                    if block_content.strip():
                        progress.update(task, description=f"翻译文本块 ({i+1}/{len(blocks)})")
                        translated_content = await self._translate_text_chunk(
                            block_content, progress, task
                        )
                        translated_blocks.append(translated_content)
                    else:
                        translated_blocks.append(block_content)

                progress.update(task, advance=1)

                if self.config.rate_limit_delay > 0:
                    await asyncio.sleep(self.config.rate_limit_delay)

        return '\n'.join(translated_blocks)

    async def translate_directory(self):
        all_files = list(self.config.source_dir.rglob("*"))
        md_files = [p for p in all_files if p.is_file() and p.suffix.lower() == ".md"]
        asset_files = [p for p in all_files if p.is_file() and p.suffix.lower() != ".md"]

        if not md_files and not asset_files:
            self.console.print("[red]错误: 在源目录中未找到文件[/red]")
            return

        self._show_file_list(md_files)

        if not self.config.auto_confirm:
            if not Confirm.ask(f"确认翻译 {len(md_files)} 个 Markdown 文件" +
                               (f" 并复制 {len(asset_files)} 个资源文件" if self.config.copy_assets else "") + "？"):
                self.console.print("[yellow]操作已取消[/yellow]")
                return

        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        semaphore = asyncio.Semaphore(self.config.max_concurrent)

        async def translate_with_semaphore(file_path: Path):
            async with semaphore:
                return await self._translate_file(file_path)

        if self.config.copy_assets and asset_files:
            await self._copy_assets(asset_files)

        self.console.print("\n[bold green]🚀 开始翻译 Markdown...[/bold green]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("总体进度", total=len(md_files))
            results = []
            for chunk_start in range(0, len(md_files), self.config.max_concurrent):
                chunk = md_files[chunk_start:chunk_start+self.config.max_concurrent]
                batch_results = await asyncio.gather(
                    *[translate_with_semaphore(f) for f in chunk],
                    return_exceptions=True
                )
                results.extend(batch_results)
                progress.update(task, advance=len(chunk))

        success_count = sum(1 for r in results if r is True)
        fail_count = len(md_files) - success_count
        self._show_summary(success_count, fail_count)

    async def _copy_assets(self, asset_files: List[Path]):
        self.console.print("[bold cyan]📦 正在复制资源文件...[/bold cyan]")
        copied = 0
        skipped = 0

        async def copy_one(src: Path):
            nonlocal copied, skipped
            rel = src.relative_to(self.config.source_dir)
            dst = self.config.output_dir / rel
            try:
                if self._should_skip(src, dst):
                    skipped += 1
                    return
                dst.parent.mkdir(parents=True, exist_ok=True)
                await asyncio.to_thread(shutil.copy2, src, dst)
                copied += 1
            except Exception as e:
                self.logger.error(f"资源复制失败: {rel} -> {dst}，原因: {e}")

        semaphore = asyncio.Semaphore(max(1, self.config.max_concurrent * 2))

        async def copy_with_semaphore(f: Path):
            async with semaphore:
                await copy_one(f)

        await asyncio.gather(*[copy_with_semaphore(f) for f in asset_files])
        self.console.print(f"✅ 资源复制完成：复制 {copied} 个，跳过 {skipped} 个")

    def _show_file_list(self, files: List[Path]):
        table = Table(title="发现的Markdown文件", show_header=True)
        table.add_column("序号", style="cyan", width=6)
        table.add_column("文件名", style="green")
        table.add_column("相对路径", style="blue")
        table.add_column("大小", style="magenta")

        for i, file in enumerate(files, 1):
            relative_path = file.relative_to(self.config.source_dir)
            size_kb = f"{file.stat().st_size / 1024:.1f} KB"
            table.add_row(str(i), file.name, str(relative_path), size_kb)

        self.console.print(table)

    def _show_summary(self, success: int, failed: int):
        total = success + failed
        panel_content = f"""
[green]✅ 成功翻译: {success} 个文件[/green]
[red]❌ 翻译失败: {failed} 个文件[/red]
[blue]📊 总计: {total} 个文件[/blue]
[yellow]📁 输出目录: {self.config.output_dir}[/yellow]
        """
        status = "成功完成" if failed == 0 else "部分完成"
        color = "green" if failed == 0 else "yellow"
        self.console.print(Panel(
            panel_content.strip(),
            title=f"[bold {color}]翻译{status}[/bold {color}]",
            border_style=color
        ))


def load_config(config_path: str) -> dict:
    """从配置文件加载配置；若不存在则生成示例"""
    if not os.path.exists(config_path):
        example_config = {
            'model_provider': 'openai',   # openai, anthropic, google
            'model_name': 'gpt-3.5-turbo',
            'api_key': 'your-api-key-here',  # 可留空，优先读环境变量
            'base_url': None,
            'max_concurrent': 3,
            'rate_limit_delay': 0.8,
            'chunk_size': 2000,
            'source_lang': 'English',
            'target_lang': 'Chinese',
            'preserve_formatting': True,
            'auto_confirm': False,
            'copy_assets': True,
            'skip_unchanged': True
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(example_config, f, default_flow_style=False, allow_unicode=True)
        print(f"已创建示例配置文件: {config_path}")
        print("提示：你也可以直接用环境变量 OPENAI_API_KEY / ANTHROPIC_API_KEY / GOOGLE_API_KEY")
        raise SystemExit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    return config_data or {}


def resolve_api_key(provider: str, api_key_in_config: Optional[str]) -> Optional[str]:
    if api_key_in_config and api_key_in_config != 'your-api-key-here':
        return api_key_in_config
    env_map = {
        'openai': 'OPENAI_API_KEY',
        'anthropic': 'ANTHROPIC_API_KEY',
        'google': 'GOOGLE_API_KEY',
    }
    env_key = env_map.get(provider.lower())
    return os.getenv(env_key) if env_key else None


def default_output_dir_for(source_dir: Path) -> Path:
    return Path.cwd() / "translate_output" / source_dir.name