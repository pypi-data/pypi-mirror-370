"""
CLI Manager - Base class for parser CLI interfaces

Strict Pydantic v2 compliance and type safety
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional, Any, Dict
import click

from .parser_manager import ParserManager, ParserManagerConfig
from .managers import ParserConfig, LoggingConfig, HTMLCleaningConfig, BrowserConfig


class CLIManager(ParserManager):
    """Base CLI manager with common CLI functionality."""
    
    def __init__(self, parser_name: str, parser_type: str, system_dir: str, 
                 bridge_enabled: bool = False, websocket_url: str = "ws://localhost:8000/ws"):
        # Create parser config
        parser_config = ParserConfig(
            parser_name=parser_name,
            parser_type=parser_type,
            system_dir=Path(system_dir)
        )
        
        # Create logging config
        logging_config = LoggingConfig(parser_name=parser_name)
        
        # Create other configs
        html_config = HTMLCleaningConfig()
        browser_config = BrowserConfig()
        
        # Create manager config
        manager_config = ParserManagerConfig(
            parser_config=parser_config,
            logging_config=logging_config,
            html_config=html_config,
            browser_config=browser_config,
            bridge_enabled=bridge_enabled
        )
        
        super().__init__(manager_config)
    
    async def run_parse_command(self, urls: Optional[List[str]] = None) -> bool:
        """Run parse command."""
        try:
            await self.initialize()
            
            if urls:
                click.echo(f"🚀 Parsing {len(urls)} URLs...")
                results = []
                for url in urls:
                    result = await self.parse_url(url)
                    results.append(result)
                
                success_count = sum(1 for r in results if r.get("success") == "true")
                click.echo(f"✅ Parse completed: {success_count}/{len(results)} URLs successful")
                return success_count > 0
            else:
                click.echo("❌ No URLs provided", err=True)
                return False
        
        except Exception as e:
            click.echo(f"❌ Parse error: {e}", err=True)
            return False
        finally:
            await self.cleanup()
    
    async def run_test_command(self) -> bool:
        """Run test command."""
        try:
            click.echo("🧪 Running test...")
            
            await self.initialize()
            click.echo("✅ Parser initialization: OK")
            
            # Test HTML cleaning
            html = "<html><body><h1>Test</h1></body></html>"
            cleaned = await self.clean_html(html)
            click.echo(f"✅ HTML cleaning: OK ({len(html)} → {len(cleaned)} chars)")
            
            click.echo("✅ All tests passed!")
            return True
        
        except Exception as e:
            click.echo(f"❌ Test failed: {e}", err=True)
            return False
        finally:
            await self.cleanup()
    
    async def run_quick_command(self, urls: List[str]) -> bool:
        """Run quick parse command."""
        try:
            click.echo(f"⚡ Quick parse of {len(urls)} URLs...")
            
            await self.initialize()
            results = []
            for url in urls:
                result = await self.parse_url(url)
                results.append(result)
            
            success_count = sum(1 for r in results if r.get("success") == "true")
            click.echo(f"✅ Quick parse completed: {success_count}/{len(results)} URLs successful")
            
            return success_count > 0
        
        except Exception as e:
            click.echo(f"❌ Quick parse error: {e}", err=True)
            return False
        finally:
            await self.cleanup()
    
    def show_status(self, config_data: Dict[str, Any]) -> None:
        """Show parser status."""
        click.echo("📊 Parser Status")
        click.echo("=" * 40)
        click.echo(f"Parser Name: {self.config.parser_name}")
        click.echo(f"Parser Type: {self.config.parser_type}")
        click.echo(f"System Dir: {self.config.system_dir}")
        click.echo(f"Bridge: {'Enabled' if self.config.bridge_enabled else 'Disabled'}")
        if self.config.bridge_enabled:
            click.echo(f"  URL: {self.config.websocket_url}")
    
    @staticmethod
    def create_config_file(config_path: Path, create_func) -> None:
        """Create configuration file."""
        try:
            create_func(config_path)
            click.echo(f"✅ Configuration file created: {config_path}")
            click.echo("   Edit the file to customize your parser settings")
        except Exception as e:
            click.echo(f"❌ Failed to create configuration: {e}", err=True)
    
    @staticmethod
    def run_async_command(coro):
        """Helper to run async command and exit with proper code."""
        success = asyncio.run(coro)
        sys.exit(0 if success else 1)
