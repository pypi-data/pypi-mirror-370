#!/usr/bin/env python3
"""
UnrealOn Browser CLI - Main entry point
Click + questionary powered command-line interface
"""

import click
from .browser_cli import browser
from .cookies_cli import cookies


@click.group()
@click.version_option(version="1.0.0", prog_name="unrealon-browser")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, verbose):
    """
    🌐 UnrealOn Browser - Enterprise browser automation with stealth capabilities

    Combines Click command structure with questionary interactive prompts
    for the best of both worlds: scriptable commands and interactive workflows.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    if verbose:
        click.echo("🔧 Verbose mode enabled")


# Add command groups
cli.add_command(browser)
cli.add_command(cookies)


@cli.command()
@click.option("--parser", default="default_parser", help="Parser name")
@click.pass_context
def interactive(ctx, parser):
    """
    🎭 Interactive mode with questionary prompts

    Launch fully interactive browser management with beautiful prompts
    """
    import asyncio
    from .interactive_mode import run_interactive_mode

    verbose = ctx.obj.get("verbose", False)
    asyncio.run(run_interactive_mode(parser, verbose))


if __name__ == "__main__":
    cli()
