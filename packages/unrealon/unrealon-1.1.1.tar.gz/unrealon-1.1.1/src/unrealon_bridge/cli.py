"""
CLI commands for unrealon_bridge.

Provides command-line interfaces for running parser bridge servers.
"""

import asyncio
import sys
import os
import time
from pathlib import Path
from typing import Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import websockets
import click

from unrealon_bridge import ParserBridgeServer
from unrealon_bridge.configs import load_bridge_config, create_sample_config, save_bridge_config
from unrealon_rpc.logging import get_logger, setup_logging_with_clear, clear_specific_log_file, resolve_log_path
from unrealon_rpc.logging.models import LogConfig

logger = get_logger(__name__)


async def run_parser_bridge_server_async(
    redis_url: str = "redis://localhost:6379/0",
    rpc_channel: str = "parser_rpc",
    pubsub_prefix: str = "parser",
    websocket_host: str = "localhost",
    websocket_port: int = 8001,
    clear_logs: bool = True
) -> None:
    """
    Run Parser Bridge Server asynchronously.
    
    Args:
        redis_url: Redis connection URL
        rpc_channel: RPC channel name
        pubsub_prefix: PubSub channel prefix
        websocket_host: WebSocket host
        websocket_port: WebSocket port
    """
    # Setup logging with file output and clear only this server's log
    log_file_path = resolve_log_path("logs/parser_bridge.log")
    log_config = LogConfig(
        file_enabled=True,
        file_path=log_file_path,
        log_level="INFO"
    )
    if clear_logs:
        clear_specific_log_file(log_file_path)
    setup_logging_with_clear(log_config, clear_logs=False)
    
    logger.info("Starting Parser Bridge Server")
    logger.info(f"Redis URL: {redis_url}")
    logger.info(f"RPC Channel: {rpc_channel}")
    logger.info(f"PubSub Prefix: {pubsub_prefix}")
    logger.info(f"WebSocket: {websocket_host}:{websocket_port}")
    
    server = ParserBridgeServer(
        redis_url=redis_url,
        rpc_channel=rpc_channel,
        pubsub_prefix=pubsub_prefix
    )
    
    # Register example command handlers
    async def example_scrape_handler(command):
        """Example handler for scrape commands."""
        logger.info(f"Processing scrape command: {command.command_id}")
        return {
            "success": "true",
            "message": f"Scrape completed for command {command.command_id}",
            "items_found": "42",
            "timestamp": command.created_at.isoformat()
        }
    
    async def example_parse_handler(command):
        """Example handler for parse commands."""
        logger.info(f"Processing parse command: {command.command_id}")
        return {
            "success": "true",
            "message": f"Parse completed for command {command.command_id}",
            "parsed_items": "15",
            "timestamp": command.created_at.isoformat()
        }
    
    async def health_handler(command):
        """Handler for health commands."""
        logger.info(f"Processing health command: {command.command_id} for parser {command.parser_id}")
        return {
            "command_type": "health",
            "status": "healthy",
            "parser_ready": "true",
            "bridge_connected": "true",
            "timestamp": command.created_at.isoformat()
        }
    
    async def status_handler(command):
        """Handler for status commands."""
        logger.info(f"Processing status command: {command.command_id} for parser {command.parser_id}")
        return {
            "command_type": "status",
            "running": "true",
            "uptime_seconds": "60",
            "total_runs": "0",
            "successful_runs": "0",
            "failed_runs": "0",
            "timestamp": command.created_at.isoformat()
        }
    
    # Register handlers
    server.register_command_handler("scrape", example_scrape_handler)
    server.register_command_handler("parse", example_parse_handler)
    server.register_command_handler("test_command", example_scrape_handler)
    server.register_command_handler("benchmark_command", example_scrape_handler)
    server.register_command_handler("throughput_test", example_parse_handler)
    server.register_command_handler("concurrent_test", example_scrape_handler)
    server.register_command_handler("health", health_handler)
    server.register_command_handler("status", status_handler)
    
    # Start server
    await server.start()
    logger.info("Parser Bridge Server started successfully")
    
    # WebSocket handler
    async def websocket_handler(websocket):
        """Handle WebSocket connections."""
        logger.info(f"New WebSocket connection from {websocket.remote_address}")
        try:
            await server.bridge.handle_websocket(websocket)
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        finally:
            logger.info("WebSocket connection closed")
    
    try:
        logger.info(f"Starting WebSocket server on {websocket_host}:{websocket_port}")
        
        # Start WebSocket server
        async with websockets.serve(websocket_handler, websocket_host, websocket_port):
            logger.info(f"WebSocket server started on {websocket_host}:{websocket_port}")
            
            # Keep server running
            while True:
                await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        logger.info("Stopping Parser Bridge Server...")
        await server.stop()
        logger.info("Parser Bridge Server stopped")


@click.command()
@click.option("--redis-url", default="redis://localhost:6379/0", help="Redis connection URL")
@click.option("--rpc-channel", default="parser_rpc", help="RPC channel name")
@click.option("--pubsub-prefix", default="parser", help="PubSub channel prefix")
@click.option("--websocket-host", default="localhost", help="WebSocket host")
@click.option("--websocket-port", type=int, default=8001, help="WebSocket port")
def run_parser_bridge_server(redis_url: str, rpc_channel: str, pubsub_prefix: str, websocket_host: str, websocket_port: int) -> None:
    """Run unrealon_bridge Parser Bridge Server."""
    try:
        asyncio.run(run_parser_bridge_server_async(
            redis_url=redis_url,
            rpc_channel=rpc_channel,
            pubsub_prefix=pubsub_prefix,
            websocket_host=websocket_host,
            websocket_port=websocket_port
        ))
    except KeyboardInterrupt:
        logger.info("Server shutdown completed")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


def _run_parser_bridge_server_with_reload_impl(
    redis_url: str = "redis://localhost:6379/0",
    rpc_channel: str = "parser_rpc",
    pubsub_prefix: str = "parser",
    websocket_host: str = "localhost",
    websocket_port: int = 8002,
    watch_dirs: Optional[list] = None
) -> None:
    """
    Run Parser Bridge Server with auto-reload on file changes.
    """
    
    if watch_dirs is None:
        # Watch current directory and src directory
        current_dir = Path.cwd()
        src_dir = current_dir / "src"
        watch_dirs = [str(current_dir), str(src_dir)] if src_dir.exists() else [str(current_dir)]
    
    class ReloadHandler(FileSystemEventHandler):
        def __init__(self):
            self.last_reload = 0
            self.reload_delay = 1.0  # Delay to avoid multiple reloads
        
        def on_modified(self, event):
            if event.is_directory:
                return
            
            # Only reload for Python files
            if not event.src_path.endswith('.py'):
                return
            
            # Avoid too frequent reloads
            current_time = time.time()
            if current_time - self.last_reload < self.reload_delay:
                return
            
            self.last_reload = current_time
            logger.info(f"File changed: {event.src_path}")
            logger.info("Restarting Parser Bridge Server...")
            
            # Restart the process
            os.execv(sys.executable, [sys.executable] + sys.argv)
    
    # Setup file watcher
    event_handler = ReloadHandler()
    observer = Observer()
    
    for watch_dir in watch_dirs:
        if os.path.exists(watch_dir):
            observer.schedule(event_handler, watch_dir, recursive=True)
            logger.info(f"Watching directory for changes: {watch_dir}")
    
    observer.start()
    
    try:
        logger.info("🔄 Auto-reload enabled - server will restart on file changes")
        # Don't clear logs on auto-reload, only on first start
        clear_logs_on_start = not os.environ.get('PARSER_BRIDGE_RELOADING', False)
        os.environ['PARSER_BRIDGE_RELOADING'] = 'true'
        asyncio.run(run_parser_bridge_server_async(
            redis_url, rpc_channel, pubsub_prefix, websocket_host, websocket_port, clear_logs_on_start
        ))
    except KeyboardInterrupt:
        logger.info("Server shutdown completed")
    finally:
        observer.stop()
        observer.join()


@click.command()
@click.option("--redis-url", default="redis://localhost:6379/0", help="Redis connection URL")
@click.option("--rpc-channel", default="parser_rpc", help="RPC channel name")
@click.option("--pubsub-prefix", default="parser", help="PubSub channel prefix")
@click.option("--websocket-host", default="localhost", help="WebSocket host")
@click.option("--websocket-port", type=int, default=8002, help="WebSocket port (dev mode)")
@click.option("--watch-dirs", multiple=True, help="Additional directories to watch for changes")
def run_parser_bridge_server_with_reload(redis_url: str, rpc_channel: str, pubsub_prefix: str, websocket_host: str, websocket_port: int, watch_dirs: tuple) -> None:
    """Run unrealon_bridge Parser Bridge Server with auto-reload (development mode)."""
    try:
        _run_parser_bridge_server_with_reload_impl(
            redis_url=redis_url,
            rpc_channel=rpc_channel,
            pubsub_prefix=pubsub_prefix,
            websocket_host=websocket_host,
            websocket_port=websocket_port,
            watch_dirs=list(watch_dirs) if watch_dirs else None
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


@click.command()
@click.option('--output', '-o', default='bridge_config.yaml', help='Output config file path')
@click.option('--force', is_flag=True, help='Overwrite existing config file')
def create_config(output: str, force: bool):
    """Create a sample bridge configuration file."""
    config_path = Path(output)
    
    if config_path.exists() and not force:
        click.echo(f"❌ Config file already exists: {config_path}")
        click.echo("Use --force to overwrite")
        sys.exit(1)
    
    try:
        # Create sample configuration
        config = create_sample_config()
        saved_path = save_bridge_config(config, config_path)
        
        click.echo(f"✅ Created sample config: {saved_path}")
        click.echo("\n📋 Configuration includes:")
        click.echo("  • Test API keys for debugging")
        click.echo("  • Development environment settings")
        click.echo("  • WebSocket on port 8002")
        click.echo("  • Redis connection settings")
        click.echo("\n🔧 Edit the config file to customize settings")
        
    except Exception as e:
        click.echo(f"❌ Failed to create config: {e}")
        sys.exit(1)


@click.group()
def cli():
    """Unrealon Bridge CLI tools."""
    pass


cli.add_command(run_parser_bridge_server, name="server")
cli.add_command(create_config, name="create-config")


if __name__ == "__main__":
    cli()
