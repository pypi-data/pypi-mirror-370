import click
from pathlib import Path
from click import pass_context
from .cli_handler import CliHandler
from srtify.core.translator import TranslatorApp
from srtify.core.settings import SettingsManager
from srtify.core.prompts import PromptsManager


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """ Gemini SRT Translator - Translate subtitle files using AI """
    if ctx.invoked_subcommand is None:
        settings_mgr = SettingsManager()
        prompts = PromptsManager()
        cli_handler = CliHandler(settings_mgr, prompts)
        cli_handler.handle_main_menu()


@cli.command()
@click.option('--input', '-i', type=click.Path(path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path),
              help='Output directory (default: from settings)')
@click.option('--language', '-l', help='Target language (default: from settings)')
@click.option('--file', '-f', help='Specific file to translate (default: all .srt files)')
@click.option('--prompt', '-p', help='Search for a specific prompt by name')
@click.option('--custom-prompt', help='Use a custom prompt')
@click.option('--batch-size', '-b', type=int, help='Batch size for translation')
@click.option('-quick', '-q', is_flag=True, help='Quick translation with default prompt')
def translate(input, output, language, file, prompt, custom_prompt, batch_size, quick):
    """ Translate SRT files from INPUT_PATH """
    settings = SettingsManager()
    prompts = PromptsManager()

    app = TranslatorApp(settings, prompts)

    options = {
        'input_path': input,
        'output_path': output,
        'language': language,
        'file': file,
        'prompt': prompt,
        'custom_prompt': custom_prompt,
        'batch_size': batch_size,
        'quick': quick
    }

    app.run_translation(options)


@cli.command()
def interactive():
    """ Start interactive translation mode ."""
    settings_mgr = SettingsManager()
    prompts = PromptsManager()
    cli_handler = CliHandler(settings_mgr, prompts)
    cli_handler.handle_main_menu()


@cli.group(invoke_without_command=True)
@pass_context
def prompts(ctx):
    """ Manage translation prompts. """
    settings_mgr = SettingsManager()
    prompts = PromptsManager()
    cli_handler = CliHandler(settings_mgr, prompts)
    ctx.ensure_object(dict)
    ctx.obj['cli_handler'] = cli_handler
    ctx.obj['prompts'] = prompts
    if ctx.invoked_subcommand is None:
        cli_handler.handle_prompts_menu()


@prompts.command(name="add")
@click.argument("new_prompt", nargs=2, type=str)
@click.pass_context
def add_prompt(ctx, new_prompt):
    """Add a new prompt."""
    prompt, description = new_prompt
    cli_handler = ctx.obj['cli_handler']
    click.echo("Saving prompt...")
    cli_handler.add_prompt(prompt_name=prompt, prompt_description=description)


@prompts.command(name="search")
@click.argument("search_term")
@click.pass_context
def search_prompts(ctx, search_term):
    """ Search for prompts by name or description. """
    prompts_manager = ctx.obj['prompts']
    results = prompts_manager.search_prompts(search_term)
    # results = prompts.search_prompts(search_term)

    if results:
        click.echo(f"Found {len(results)} prompts matching {search_term}...")
        for name, description in results.items():
            click.echo(f"   {name}: {description[:100]}{'...' if len(description) else ''}")
    else:
        click.echo(f"No prompts found matching '{search_term}'")


@cli.command()
def status():
    """ Show current configuration status. """
    settings_mgr = SettingsManager()
    prompts = PromptsManager()

    click.echo("=== Configuration Status ===")
    summary = settings_mgr.get_settings_summary()
    for key, value in summary.items():
        click.echo(f"  {key}: {value}")

    click.echo(f"\nPrompts: {prompts.count_prompts()} total")

def register_settings_commands():
    from .settings_commands import settings
    cli.add_command(settings)

register_settings_commands()