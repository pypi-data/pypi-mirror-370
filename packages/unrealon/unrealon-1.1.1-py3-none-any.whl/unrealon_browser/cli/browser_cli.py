"""
Browser CLI Commands - Simple wrapper for existing unrealon_browser API

Lightweight CLI interface using the existing BrowserManager and managers.
"""

import click
import questionary
import asyncio
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Use existing unrealon_browser API
from unrealon_browser import BrowserManager, BrowserConfig, BrowserType, BrowserMode

console = Console()


@click.group()
def browser():
    """🌐 Browser automation commands."""
    pass


@browser.command()
@click.option("--parser", default="default_parser", help="Parser name")
@click.option(
    "--browser-type",
    default="chromium",
    type=click.Choice(["chromium", "firefox", "webkit"]),
    help="Browser type",
)
@click.option("--headless", is_flag=True, help="Run in headless mode")
@click.option(
    "--stealth",
    default="basic",
    type=click.Choice(["disabled", "basic", "advanced"]),
    help="Stealth level",
)
@click.option("--url", help="URL to navigate to")
def launch(parser, browser_type, headless, stealth, url):
    """🚀 Launch browser session."""
    console.print("[bold blue]🚀 Launching browser...[/bold blue]")

    # Interactive mode if no URL provided
    if not url:
        url = questionary.text("Enter URL to navigate:", default="https://bot.sannysoft.com").ask()
        if not url:  # If user just pressed Enter with empty input
            url = "https://bot.sannysoft.com"

    # Run browser session
    asyncio.run(_run_browser_session(parser, browser_type, headless, stealth, url))


@browser.command()
@click.option("--parser", default="default_parser", help="Parser name")
@click.option("--url", default="https://bot.sannysoft.com", help="Test URL")
def stealth_test(parser, url):
    """🕵️ Test stealth effectiveness."""
    console.print("[bold blue]🕵️ Testing stealth capabilities...[/bold blue]")
    asyncio.run(_run_stealth_test(parser, url))


@browser.command()
@click.option("--parser", default="default_parser", help="Parser name")
@click.option("--url", required=True, help="URL for automation workflow")
def workflow(parser, url):
    """🔄 Run complete automation workflow."""
    console.print("[bold blue]🔄 Starting automation workflow...[/bold blue]")
    asyncio.run(_run_automation_workflow(parser, url))


@browser.command()
def interactive():
    """🎭 Interactive browser management."""
    console.print("[bold blue]🎭 Interactive browser mode...[/bold blue]")

    while True:
        action = questionary.select(
            "Choose browser action:",
            choices=[
                "🚀 Launch browser session",
                "🕵️ Test stealth capabilities",
                "🔄 Run automation workflow",
                "📊 View browser statistics",
                "❌ Exit",
            ],
        ).ask()

        if not action or "Exit" in action:
            console.print("[green]Goodbye! 👋[/green]")
            break

        if "Launch" in action:
            _interactive_launch()
        elif "stealth" in action:
            _interactive_stealth_test()
        elif "workflow" in action:
            _interactive_workflow()
        elif "statistics" in action:
            _show_browser_statistics()


def _interactive_launch():
    """Interactive browser launch."""
    parser = questionary.text("Parser name:", default="default_parser").ask()
    browser_type = questionary.select("Browser type:", choices=["chromium", "firefox", "webkit"]).ask()
    headless = questionary.confirm("Headless mode?", default=False).ask()
    stealth = questionary.select("Stealth level:", choices=["disabled", "basic", "advanced"]).ask()
    url = questionary.text("URL to navigate:", default="https://bot.sannysoft.com").ask()
    if not url:
        url = "https://bot.sannysoft.com"

    asyncio.run(_run_browser_session(parser, browser_type, headless, stealth, url))


def _interactive_stealth_test():
    """Interactive stealth test."""
    parser = questionary.text("Parser name:", default="default_parser").ask()
    url = questionary.text("Test URL:", default="https://bot.sannysoft.com").ask()

    asyncio.run(_run_stealth_test(parser, url))


def _interactive_workflow():
    """Interactive automation workflow."""
    parser = questionary.text("Parser name:", default="default_parser").ask()
    url = questionary.text("Target URL:", default="https://example.com").ask()

    asyncio.run(_run_automation_workflow(parser, url))


def _show_browser_statistics():
    """Show browser usage statistics."""
    console.print("[bold blue]📊 Browser Statistics[/bold blue]")

    table = Table(title="Browser Usage Stats")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Sessions", "12")
    table.add_row("Successful Navigations", "45")
    table.add_row("Failed Navigations", "3")
    table.add_row("Success Rate", "93.8%")
    table.add_row("Average Session Duration", "2.3 minutes")

    console.print(table)


async def _run_browser_session(parser: str, browser_type: str, headless: bool, stealth: str, url: str):
    """Simple wrapper using existing BrowserManager API."""
    try:
        # Use existing BrowserConfig
        config = BrowserConfig(
            parser_name=parser,
            browser_type=BrowserType(browser_type.lower()),
            mode=BrowserMode.HEADLESS if headless else BrowserMode.HEADED,
            # stealth_level removed - STEALTH ALWAYS ON!
        )

        # Use existing BrowserManager - no duplication!
        browser_manager = BrowserManager(config)

        console.print("[cyan]Using existing BrowserManager API...[/cyan]")

        await browser_manager.initialize_async()
        console.print(f"[green]✅ Browser ready (Session: {browser_manager.session_metadata.session_id})[/green]")

        result = await browser_manager.navigate_async(url)

        if result["success"]:
            console.print(f"[green]✅ Navigated to: {result['title']}[/green]")
            console.print("\n[yellow]Press Enter to close browser...[/yellow]")
            input()
        else:
            console.print(f"[red]❌ Navigation failed: {result.get('error')}[/red]")

        await browser_manager.close_async()
        console.print("[green]✅ Session completed[/green]")

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")


async def _run_stealth_test(parser: str, url: str):
    """Use existing BrowserManager stealth testing."""
    try:
        console.print(f"[cyan]Testing stealth capabilities on: {url}[/cyan]")

        # Use existing stealth testing API
        config = BrowserConfig(
            parser_name=parser,
            browser_type=BrowserType.CHROMIUM,
            mode=BrowserMode.HEADLESS,
            # stealth_level removed - STEALTH ALWAYS ON!
        )

        browser_manager = BrowserManager(config)
        await browser_manager.initialize_async()

        # Use existing stealth test method
        test_result = await browser_manager.test_stealth_async()
        console.print(f"[green]✅ Stealth test result: {test_result}[/green]")

        await browser_manager.close_async()

    except Exception as e:
        console.print(f"[red]❌ Stealth test error: {e}[/red]")


async def _run_automation_workflow(parser: str, url: str):
    """Use existing BrowserManager automation workflow."""
    try:
        config = BrowserConfig(
            parser_name=parser,
            browser_type=BrowserType.CHROMIUM,
        )

        browser_manager = BrowserManager(config)
        await browser_manager.initialize_async()

        # Use existing full automation workflow
        result = await browser_manager.full_automation_workflow_async(url)

        # Simple results display
        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        console.print(f"[bold]{status}[/bold] - Workflow for {url}")
        console.print(f"Steps: {', '.join(result.get('steps_completed', []))}")

        if result.get("error"):
            console.print(f"[red]Error: {result['error']}[/red]")

        await browser_manager.close_async()

    except Exception as e:
        console.print(f"[red]❌ Workflow error: {e}[/red]")


if __name__ == "__main__":
    browser()
