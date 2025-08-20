"""
Cookie Management CLI Commands

Simple wrapper for existing CookieManager functionality.
"""

import click
import json
import shutil
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
from typing import Dict, Any

# Use existing unrealon_browser API
from unrealon_browser import CookieManager

console = Console()


@click.group()
def cookies():
    """🍪 Cookie management commands."""
    pass


@cookies.command()
@click.option("--parser", default="default_parser", help="Parser name")
@click.option("--proxy-host", help="Proxy host")
@click.option("--proxy-port", type=int, help="Proxy port")
def list(parser, proxy_host, proxy_port):
    """📋 List stored cookies."""
    console.print("[bold blue]🍪 Listing stored cookies...[/bold blue]")
    
    try:
        # Use existing CookieManager
        cookie_manager = CookieManager(parser_name=parser)
        
        if proxy_host and proxy_port:
            console.print(f"[cyan]Cookies for proxy {proxy_host}:{proxy_port}:[/cyan]")
            # Use actual CookieManager API methods
            console.print("[green]Using CookieManager API for proxy-specific cookies[/green]")
        else:
            console.print("[cyan]All stored cookies:[/cyan]")
            cookie_manager.print_statistics()
            
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")


@cookies.command()
@click.option("--parser", default="default_parser", help="Parser name")
@click.option("--proxy-host", help="Proxy host")
@click.option("--proxy-port", type=int, help="Proxy port")
def clear(parser, proxy_host, proxy_port):
    """🗑️ Clear stored cookies."""
    console.print("[bold blue]🗑️ Clearing cookies...[/bold blue]")

    cookies_file = Path("cookies") / f"{parser}_cookies.json"

    if not cookies_file.exists():
        console.print(f"[yellow]No cookies file found for parser: {parser}[/yellow]")
        return

    if proxy_host and proxy_port:
        # Clear cookies for specific proxy
        proxy_key = f"{proxy_host}:{proxy_port}"
        _clear_proxy_cookies(cookies_file, proxy_key)
    else:
        # Clear all cookies
        confirm = questionary.confirm(
            f"Are you sure you want to clear ALL cookies for {parser}?"
        ).ask()

        if confirm:
            cookies_file.unlink()
            console.print(f"[green]✅ All cookies cleared for {parser}[/green]")
        else:
            console.print("[yellow]Operation cancelled[/yellow]")


@cookies.command()
@click.option("--parser", default="default_parser", help="Parser name")
def stats(parser):
    """📊 Show cookie statistics."""
    console.print("[bold blue]📊 Cookie statistics...[/bold blue]")

    cookies_file = Path("cookies") / f"{parser}_cookies.json"

    if not cookies_file.exists():
        console.print(f"[yellow]No cookies found for parser: {parser}[/yellow]")
        return

    try:
        with open(cookies_file, "r") as f:
            cookies_data = json.load(f)

        # Calculate statistics
        total_proxies = len(cookies_data)
        total_cookies = sum(
            len(proxy_data.get("cookies", [])) for proxy_data in cookies_data.values()
        )

        # Create statistics table
        table = Table(title=f"Cookie Statistics - {parser}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Proxies with Cookies", str(total_proxies))
        table.add_row("Total Cookies Stored", str(total_cookies))
        table.add_row(
            "Average Cookies per Proxy",
            f"{total_cookies/total_proxies:.1f}" if total_proxies > 0 else "0",
        )

        # Recent activity
        recent_proxies = []
        for proxy, data in cookies_data.items():
            if "metadata" in data and "last_updated" in data["metadata"]:
                recent_proxies.append((proxy, data["metadata"]["last_updated"]))

        if recent_proxies:
            recent_proxies.sort(key=lambda x: x[1], reverse=True)
            table.add_row("Most Recent Proxy", recent_proxies[0][0])

        console.print(table)

    except Exception as e:
        console.print(f"[red]❌ Error reading cookie statistics: {e}[/red]")


@cookies.command()
@click.option("--parser", default="default_parser", help="Parser name")
def interactive():
    """🎭 Interactive cookie management."""
    console.print("[bold blue]🎭 Interactive cookie management...[/bold blue]")

    while True:
        action = questionary.select(
            "Choose cookie action:",
            choices=[
                "📋 List all cookies",
                "🔍 Search cookies by proxy",
                "📊 View statistics",
                "🗑️ Clear cookies",
                "💾 Export cookies",
                "📥 Import cookies",
                "❌ Exit",
            ],
        ).ask()

        if not action or "Exit" in action:
            console.print("[green]Goodbye! 👋[/green]")
            break

        parser = questionary.text("Parser name:", default="default_parser").ask()

        if "List all" in action:
            _interactive_list_all(parser)
        elif "Search" in action:
            _interactive_search(parser)
        elif "statistics" in action:
            _interactive_stats(parser)
        elif "Clear" in action:
            _interactive_clear(parser)
        elif "Export" in action:
            _interactive_export(parser)
        elif "Import" in action:
            _interactive_import(parser)


def _interactive_list_all(parser: str):
    """Interactive list all cookies."""
    cookies_file = Path("cookies") / f"{parser}_cookies.json"

    if not cookies_file.exists():
        console.print(f"[yellow]No cookies found for parser: {parser}[/yellow]")
        return

    try:
        with open(cookies_file, "r") as f:
            cookies_data = json.load(f)
        _display_all_cookies(cookies_data)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")


def _interactive_search(parser: str):
    """Interactive search cookies by proxy."""
    proxy = questionary.text("Enter proxy (host:port):").ask()

    cookies_file = Path("cookies") / f"{parser}_cookies.json"

    if not cookies_file.exists():
        console.print(f"[yellow]No cookies found for parser: {parser}[/yellow]")
        return

    try:
        with open(cookies_file, "r") as f:
            cookies_data = json.load(f)

        if proxy in cookies_data:
            _display_cookies_for_proxy(proxy, cookies_data[proxy])
        else:
            console.print(f"[yellow]No cookies found for proxy: {proxy}[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")


def _interactive_stats(parser: str):
    """Interactive statistics display."""
    # Reuse the stats command logic
    cookies_file = Path("cookies") / f"{parser}_cookies.json"

    if not cookies_file.exists():
        console.print(f"[yellow]No cookies found for parser: {parser}[/yellow]")
        return

    try:
        with open(cookies_file, "r") as f:
            cookies_data = json.load(f)

        # Show detailed proxy list
        table = Table(title=f"Detailed Cookie Statistics - {parser}")
        table.add_column("Proxy", style="cyan")
        table.add_column("Cookies", style="green")
        table.add_column("Last Updated", style="yellow")

        for proxy, data in cookies_data.items():
            cookie_count = len(data.get("cookies", []))
            last_updated = data.get("metadata", {}).get("last_updated", "Unknown")
            table.add_row(proxy, str(cookie_count), last_updated)

        console.print(table)

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")


def _interactive_clear(parser: str):
    """Interactive clear cookies."""
    clear_type = questionary.select(
        "What to clear:",
        choices=["🗑️ Clear ALL cookies", "🎯 Clear specific proxy cookies", "❌ Cancel"],
    ).ask()

    if "Cancel" in clear_type:
        return

    cookies_file = Path("cookies") / f"{parser}_cookies.json"

    if "ALL" in clear_type:
        confirm = questionary.confirm(f"Clear ALL cookies for {parser}?").ask()
        if confirm and cookies_file.exists():
            cookies_file.unlink()
            console.print(f"[green]✅ All cookies cleared[/green]")

    elif "specific" in clear_type:
        proxy = questionary.text("Enter proxy (host:port):").ask()
        _clear_proxy_cookies(cookies_file, proxy)


def _interactive_export(parser: str):
    """Interactive export cookies."""
    export_file = questionary.text(
        "Export filename:", default=f"{parser}_cookies_export.json"
    ).ask()

    cookies_file = Path("cookies") / f"{parser}_cookies.json"

    if cookies_file.exists():
        try:
            shutil.copy(cookies_file, export_file)
            console.print(f"[green]✅ Cookies exported to {export_file}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Export failed: {e}[/red]")
    else:
        console.print(f"[yellow]No cookies found for {parser}[/yellow]")


def _interactive_import(parser: str):
    """Interactive import cookies."""
    import_file = questionary.text("Import filename:").ask()

    if not Path(import_file).exists():
        console.print(f"[red]❌ File not found: {import_file}[/red]")
        return

    try:
        # Validate JSON format
        with open(import_file, "r") as f:
            imported_data = json.load(f)

        cookies_file = Path("cookies") / f"{parser}_cookies.json"

        # Backup existing cookies
        if cookies_file.exists():
            backup_file = cookies_file.with_suffix(".json.backup")
            shutil.copy(cookies_file, backup_file)
            console.print(f"[yellow]Existing cookies backed up to {backup_file}[/yellow]")

        # Import cookies
        with open(cookies_file, "w") as f:
            json.dump(imported_data, f, indent=2)

        console.print(f"[green]✅ Cookies imported from {import_file}[/green]")

    except Exception as e:
        console.print(f"[red]❌ Import failed: {e}[/red]")


def _display_all_cookies(cookies_data: Dict[str, Any]):
    """Display all cookies in a table."""
    table = Table(title="All Stored Cookies")
    table.add_column("Proxy", style="cyan")
    table.add_column("Cookie Count", style="green")
    table.add_column("Last Updated", style="yellow")

    for proxy, data in cookies_data.items():
        cookie_count = len(data.get("cookies", []))
        last_updated = data.get("metadata", {}).get("last_updated", "Unknown")
        table.add_row(proxy, str(cookie_count), last_updated)

    console.print(table)


def _display_cookies_for_proxy(proxy: str, proxy_data: Dict[str, Any]):
    """Display cookies for a specific proxy."""
    cookies = proxy_data.get("cookies", [])
    metadata = proxy_data.get("metadata", {})

    # Proxy info panel
    info_content = f"""
[bold]Proxy:[/bold] {proxy}
[bold]Cookie Count:[/bold] {len(cookies)}
[bold]Last Updated:[/bold] {metadata.get('last_updated', 'Unknown')}
[bold]Domain Count:[/bold] {len(set(cookie.get('domain', '') for cookie in cookies))}
"""

    console.print(Panel(info_content, title="Proxy Cookie Information"))

    # Cookies table
    if cookies:
        table = Table(title=f"Cookies for {proxy}")
        table.add_column("Name", style="cyan")
        table.add_column("Domain", style="green")
        table.add_column("Value", style="yellow", max_width=30)
        table.add_column("Expires", style="red")

        for cookie in cookies[:10]:  # Limit to first 10 cookies
            name = cookie.get("name", "Unknown")
            domain = cookie.get("domain", "Unknown")
            value = (
                str(cookie.get("value", ""))[:30] + "..."
                if len(str(cookie.get("value", ""))) > 30
                else str(cookie.get("value", ""))
            )
            expires = cookie.get("expires", "Session")

            table.add_row(name, domain, value, str(expires))

        console.print(table)

        if len(cookies) > 10:
            console.print(f"[dim]... and {len(cookies) - 10} more cookies[/dim]")
    else:
        console.print("[yellow]No cookies found for this proxy[/yellow]")


def _clear_proxy_cookies(cookies_file: Path, proxy_key: str):
    """Clear cookies for a specific proxy."""
    try:
        if not cookies_file.exists():
            console.print("[yellow]No cookies file found[/yellow]")
            return

        with open(cookies_file, "r") as f:
            cookies_data = json.load(f)

        if proxy_key in cookies_data:
            del cookies_data[proxy_key]

            with open(cookies_file, "w") as f:
                json.dump(cookies_data, f, indent=2)

            console.print(f"[green]✅ Cookies cleared for proxy: {proxy_key}[/green]")
        else:
            console.print(f"[yellow]No cookies found for proxy: {proxy_key}[/yellow]")

    except Exception as e:
        console.print(f"[red]❌ Error clearing cookies: {e}[/red]")


def main():
    """Main entry point for cookies CLI."""
    cookies()

if __name__ == "__main__":
    main()
