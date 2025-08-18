import argparse
import asyncio
from pathlib import Path
from rich.panel import Panel
from rich.console import Console

from .translation import (
    TranslationConfig,
    MarkdownTranslator,
    load_config,
    resolve_api_key,
    default_output_dir_for,
)
from . import __version__

async def _async_main():
    parser = argparse.ArgumentParser(prog="md-translate", description="Markdown 文件翻译工具")
    parser.add_argument('source_dir', help='源文件目录')
    parser.add_argument('output_dir', nargs='?', help='输出目录（可选，不填则默认 ./translate_output/<源目录名>）')
    parser.add_argument('--config', '-c', default='config.yaml', help='配置文件路径')
    parser.add_argument('--provider', help='模型提供商 (openai/anthropic/google)')
    parser.add_argument('--model', help='模型名称')
    parser.add_argument('--api-key', help='API密钥（不填则尝试读取环境变量）')
    parser.add_argument('-y', '--yes', action='store_true', help='跳过确认，自动执行')
    parser.add_argument('--force', action='store_true', help='强制重译，忽略增量跳过')
    parser.add_argument('--no-assets', action='store_true', help='不复制非 .md 资源文件')
    parser.add_argument('-V', '--version', action='version', version=f"%(prog)s {__version__}")

    args = parser.parse_args()

    src = Path(args.source_dir).resolve()
    dst = Path(args.output_dir).resolve() if args.output_dir else default_output_dir_for(src)

    # 加载配置
    config_data = load_config(args.config)

    # 应用命令行覆盖（仅在显式传入时）
    default_copy_assets = bool(config_data.get('copy_assets', True))
    default_skip_unchanged = bool(config_data.get('skip_unchanged', True))
    copy_assets = False if args.no_assets else default_copy_assets
    skip_unchanged = False if args.force else default_skip_unchanged

    # 创建配置对象
    provider = (args.provider or config_data.get('model_provider', 'openai'))
    config = TranslationConfig(
        source_dir=src,
        output_dir=dst,
        model_provider=provider,
        model_name=(args.model or config_data.get('model_name', 'gpt-3.5-turbo')),
        api_key=resolve_api_key(provider, args.api_key or config_data.get('api_key')),
        base_url=config_data.get('base_url'),
        max_concurrent=int(config_data.get('max_concurrent', 3)),
        rate_limit_delay=float(config_data.get('rate_limit_delay', 0.8)),
        chunk_size=int(config_data.get('chunk_size', 2000)),
        source_lang=config_data.get('source_lang', 'English'),
        target_lang=config_data.get('target_lang', 'Chinese'),
        preserve_formatting=bool(config_data.get('preserve_formatting', True)),
        auto_confirm=bool(args.yes or config_data.get('auto_confirm', False)),
        copy_assets=copy_assets,
        skip_unchanged=skip_unchanged
    )

    # 验证配置
    if not config.source_dir.exists():
        print(f"错误: 源目录不存在: {config.source_dir}")
        raise SystemExit(1)

    if not config.api_key:
        print("错误: 未找到可用的 API 密钥（可在配置文件设置，或使用环境变量 OPENAI_API_KEY/ANTHROPIC_API_KEY/GOOGLE_API_KEY）")
        raise SystemExit(1)

    translator = MarkdownTranslator(config)
    console = Console()
    console.print(Panel.fit(
        "[bold blue]Markdown翻译工具[/bold blue]\n"
        f"源目录: {config.source_dir}\n"
        f"输出目录: {config.output_dir}\n"
        f"模型: {config.model_provider}/{config.model_name}\n"
        f"复制资源: {'是' if config.copy_assets else '否'} | "
        f"增量跳过: {'是' if config.skip_unchanged else '否'}",
        border_style="blue"
    ))

    await translator.translate_directory()

def cli():
    try:
        asyncio.run(_async_main())
    except KeyboardInterrupt:
        print("\n已取消。")