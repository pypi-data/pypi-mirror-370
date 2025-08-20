import click
from srtify.cli.commands import cli
from srtify.cli.cli_handler import CliHandler
from srtify.core.prompts import PromptsManager
from srtify.core.settings import SettingsManager

@click.group(invoke_without_command=True)
@click.pass_context
def settings(ctx):
    """ Configure application settings. """
    settings_mgs = SettingsManager()
    prompts = PromptsManager()
    cli_handler = CliHandler(settings_mgs, prompts)
    ctx.ensure_object(dict)
    ctx.obj['cli_handler'] = cli_handler
    if ctx.invoked_subcommand is None:
        cli_handler.handle_settings_menu()


@settings.command()
@click.argument("api_key")
@click.pass_context
def set_api_key(ctx, api_key):
    cli_handler = ctx.obj['cli_handler']
    click.echo(f"Setting API key to {api_key}")
    cli_handler.set_api_key(api_key)


@settings.command()
@click.argument("language")
@click.pass_context
def set_language(ctx, language):
    cli_handler =  ctx.obj['cli_handler']
    click.echo(f"Setting language to {language}")
    cli_handler.set_language(language)


@settings.command()
@click.argument("batch_size")
@click.pass_context
def set_batch_size(ctx, batch_size):
    cli_handler =  ctx.obj['cli_handler']
    click.echo(f"Setting batch size to {batch_size}")
    cli_handler.set_batch_size(batch_size)