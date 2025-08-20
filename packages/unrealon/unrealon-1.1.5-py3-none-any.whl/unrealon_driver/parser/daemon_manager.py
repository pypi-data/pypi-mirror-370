"""
Daemon Manager - Base class for parser daemons

Strict Pydantic v2 compliance and type safety
"""

import asyncio
import signal
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Callable, Awaitable
from pydantic import BaseModel, Field

from .parser_manager import ParserManager, ParserManagerConfig
from .managers import ParserConfig
from unrealon_driver.models import (
    RegistrationMessage, CommandMessage, CommandResponseMessage, 
    StatusMessage, HeartbeatMessage, MessageType,
    BridgeRegistrationMessage, BridgeRegistrationPayload
)
from unrealon_driver.html_analyzer import HTMLCleaningConfig
from unrealon_driver.websocket import WebSocketClient, WebSocketConfig
from unrealon_browser.dto.models.config import BrowserConfig


class DaemonStatus(BaseModel):
    """Daemon status information."""

    running: bool = Field(..., description="Whether daemon is running")
    parser_id: str = Field(..., description="Parser identifier")
    started_at: datetime = Field(..., description="Daemon start time")
    uptime_seconds: float = Field(..., description="Uptime in seconds")
    schedule_enabled: bool = Field(default=False, description="Whether scheduling is active")
    next_run_at: Optional[datetime] = Field(default=None, description="Next scheduled run")
    total_runs: int = Field(default=0, description="Total completed runs")
    successful_runs: int = Field(default=0, description="Successful runs")
    failed_runs: int = Field(default=0, description="Failed runs")


class DaemonManager(ParserManager):
    """Base daemon manager with scheduling and status display."""

    def __init__(self, parser_name: str, parser_type: str, system_dir: str, bridge_enabled: bool = False):
        # Create parser config
        parser_config = ParserConfig(parser_name=parser_name, parser_type=parser_type, system_dir=Path(system_dir))

        # Create configs
        html_config = HTMLCleaningConfig()

        # Create manager config
        manager_config = ParserManagerConfig(
            parser_config=parser_config, 
            html_config=html_config, 
            bridge_enabled=bridge_enabled,
            console_enabled=True,
            file_enabled=True
        )

        super().__init__(manager_config)

        # Daemon state
        self.running = False
        self.started_at: Optional[datetime] = None
        self.next_run_at: Optional[datetime] = None

        # Statistics
        self.total_runs = 0
        self.successful_runs = 0
        self.failed_runs = 0

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # WebSocket bridge connection
        self.bridge_enabled = bridge_enabled
        self.websocket_client: Optional[WebSocketClient] = None
        
        # Registration status
        self.registered = False
        
        # Command handlers registry
        self.command_handlers: dict[str, Callable[[dict[str, str]], Awaitable[dict[str, str]]]] = {}
        
        # Register built-in commands
        self._register_builtin_commands()

    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals."""
        self.logger.info(f"🛑 Received signal {signum}, shutting down...")
        self.running = False

    # RPC methods removed - commands handled through WebSocket bridge

    async def start_daemon(self, schedule_enabled: bool = False, interval_minutes: Optional[int] = None) -> bool:
        """Start the daemon."""
        try:
            self.logger.info("🚀 Starting daemon...")
            self.running = True
            self.started_at = datetime.now()

            # Initialize parser
            await self.initialize()

            # Connect to WebSocket bridge
            if self.bridge_enabled:
                bridge_connected = await self._connect_to_bridge()
                if not bridge_connected:
                    self.logger.warning("⚠️ Failed to connect to bridge, continuing without WebSocket commands")
                else:
                    # Register daemon with bridge server
                    self.logger.info("🔗 Attempting to register with bridge server...")
                    registration_success = await self._register_with_bridge()
                    if not registration_success:
                        self.logger.warning("⚠️ Failed to register with bridge server")

            # Calculate next run if scheduling enabled
            if schedule_enabled and interval_minutes:
                self._calculate_next_run(interval_minutes)

            # Start main loop
            await self._daemon_loop(schedule_enabled, interval_minutes)

            return True

        except Exception as e:
            self.logger.error(f"❌ Daemon startup failed: {e}")
            return False
        finally:
            await self.cleanup()

    def _calculate_next_run(self, interval_minutes: int) -> None:
        """Calculate next scheduled run time."""
        now = datetime.now()
        self.next_run_at = now + timedelta(minutes=interval_minutes)

    async def _daemon_loop(self, schedule_enabled: bool, interval_minutes: Optional[int]) -> None:
        """Main daemon loop."""
        self.logger.info("🔄 Daemon loop started")

        if schedule_enabled and self.next_run_at:
            self.logger.info(f"⏰ Next run: {self.next_run_at.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            self.logger.info("📋 Manual mode")

        last_status_update = time.time()

        while self.running:
            try:
                current_time = time.time()

                # Update status every second
                if current_time - last_status_update >= 1.0:
                    self._display_status(schedule_enabled)
                    last_status_update = current_time

                # Check for scheduled run
                if self._should_run_now():
                    await self._execute_run()
                    if interval_minutes:
                        self._calculate_next_run(interval_minutes)

                await asyncio.sleep(0.1)

            except Exception as e:
                self.logger.error(f"❌ Daemon loop error: {e}")
                await asyncio.sleep(1)

    def _display_status(self, schedule_enabled: bool) -> None:
        """Display live status."""
        if not self.running:
            return

        # Clear previous lines
        print("\033[2K\033[1A" * 3, end="")

        now = datetime.now()
        uptime = (now - self.started_at).total_seconds() if self.started_at else 0

        print(f"🕐 {now.strftime('%H:%M:%S')} | ⏱️  Uptime: {int(uptime//3600):02d}:{int((uptime%3600)//60):02d}:{int(uptime%60):02d}")

        # Schedule status
        if self.next_run_at and schedule_enabled:
            seconds_until = (self.next_run_at - now).total_seconds()
            if seconds_until > 0:
                hours = int(seconds_until // 3600)
                minutes = int((seconds_until % 3600) // 60)
                seconds = int(seconds_until % 60)
                print(f"⏰ Next run in: {hours:02d}:{minutes:02d}:{seconds:02d} | 📊 Runs: {self.successful_runs}✅ {self.failed_runs}❌")
            else:
                print(f"🚀 Running now... | 📊 Runs: {self.successful_runs}✅ {self.failed_runs}❌")
        else:
            print(f"📋 Manual mode | 📊 Runs: {self.successful_runs}✅ {self.failed_runs}❌")

        status = "🟢 RUNNING" if self.running else "🔴 STOPPED"
        print(f"{status} | 💾 System: {self.config.parser_config.system_dir}")

    def _should_run_now(self) -> bool:
        """Check if should run now."""
        if not self.next_run_at:
            return False
        return datetime.now() >= self.next_run_at

    async def _execute_run(self) -> None:
        """Execute a parsing run - override in subclass."""
        self.logger.info("🚀 Starting parsing run...")

        try:
            # Default implementation - override in subclass
            result = await self.parse_url("https://example.com")

            self.total_runs += 1

            if result.get("success") == "true":
                self.successful_runs += 1
                self.logger.info("✅ Run completed successfully")
            else:
                self.failed_runs += 1
                self.logger.error("❌ Run failed")

        except Exception as e:
            self.failed_runs += 1
            self.logger.error(f"❌ Run exception: {e}")

    def get_status(self) -> DaemonStatus:
        """Get daemon status."""
        now = datetime.now()
        uptime = (now - self.started_at).total_seconds() if self.started_at else 0

        return DaemonStatus(
            running=self.running,
            parser_id=self.config.parser_config.parser_name,
            started_at=self.started_at or now,
            uptime_seconds=uptime,
            schedule_enabled=bool(self.next_run_at),
            next_run_at=self.next_run_at,
            total_runs=self.total_runs,
            successful_runs=self.successful_runs,
            failed_runs=self.failed_runs,
        )

    async def cleanup(self):
        """Cleanup daemon resources."""
        # Disconnect from bridge
        await self._disconnect_from_bridge()
        
        # Parent cleanup
        await super().cleanup()
    
    # ==========================================
    # WEBSOCKET BRIDGE MANAGEMENT
    # ==========================================
    
    async def _connect_to_bridge(self) -> bool:
        """Connect to WebSocket bridge server."""
        if not self.bridge_enabled:
            return True
            
        try:
            self.logger.info(f"🔌 Connecting to bridge: {self.config.parser_config.websocket_url}")
            
            # Create WebSocket config
            ws_config = WebSocketConfig(
                url=self.config.parser_config.websocket_url,
                parser_id=self.config.parser_config.parser_name,
                reconnect_interval=5.0,
                max_reconnect_attempts=10
            )
            
            # Create and connect WebSocket client
            self.websocket_client = WebSocketClient(ws_config)
            
            # Add command handler
            self.websocket_client.add_message_handler("command", self._handle_websocket_command)
            
            success = await self.websocket_client.connect()
            if success:
                self.logger.info("✅ Connected to bridge server")
                return True
            else:
                self.logger.error("❌ Failed to connect to bridge server")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to bridge: {e}")
            return False
    
    async def _register_with_bridge(self) -> bool:
        """Register daemon with bridge server via WebSocket."""
        if not self.websocket_client or not self.websocket_client.connected:
            self.logger.warning("⚠️ Cannot register - WebSocket not connected")
            return False
            
        try:
            # Create registration message using Pydantic models
            payload = BridgeRegistrationPayload(
                client_type="daemon",
                parser_id=self.config.parser_config.parser_name,
                version="1.0.0",
                capabilities=["parse", "search", "status", "health"]
            )
            
            registration_message = BridgeRegistrationMessage(payload=payload)
            
            success = await self.websocket_client.send_message(registration_message.model_dump())
            if success:
                self.registered = True
                self.logger.info(f"✅ Registered daemon with bridge server: {self.config.parser_config.parser_name}")
                return True
            else:
                self.logger.error("❌ Failed to send registration message")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register with bridge: {e}")
            return False
    
    async def _disconnect_from_bridge(self):
        """Disconnect from WebSocket bridge."""
        if self.websocket_client:
            try:
                await self.websocket_client.disconnect()
                self.logger.info("🔌 Disconnected from bridge")
            except Exception as e:
                self.logger.error(f"❌ Error disconnecting from bridge: {e}")
            finally:
                self.websocket_client = None
                self.registered = False
    

    
    async def _handle_websocket_command(self, message_data: dict[str, str]):
        """Handle incoming WebSocket command."""
        try:
            # Parse command message using Pydantic model
            command_msg = CommandMessage.model_validate(message_data)
            
            self.logger.info(f"📨 Received command: {command_msg.command_type} (id: {command_msg.command_id})")
            
            # Find and execute command handler
            if command_msg.command_type in self.command_handlers:
                result = await self.command_handlers[command_msg.command_type](command_msg.parameters)
                
                # Send success response using Pydantic model
                response = CommandResponseMessage(
                    command_id=command_msg.command_id,
                    success=True,
                    result_data=result
                )
                await self.websocket_client.send_message(response.model_dump())
                self.logger.info(f"✅ Command {command_msg.command_type} completed")
                
            else:
                raise ValueError(f"Unknown command type: {command_msg.command_type}")
                
        except Exception as e:
            self.logger.error(f"❌ Command failed: {e}")
            
            # Send error response using Pydantic model
            command_id = message_data.get("command_id", "unknown")
            response = CommandResponseMessage(
                command_id=command_id,
                success=False,
                error=str(e)
            )
            await self.websocket_client.send_message(response.model_dump())
    

    
    # ==========================================
    # COMMAND SYSTEM
    # ==========================================
    
    def register_command(self, command_type: str, handler: Callable[[dict[str, str]], Awaitable[dict[str, str]]]):
        """Register a command handler."""
        self.command_handlers[command_type] = handler
        self.logger.info(f"🔧 Registered command handler: {command_type}")
    
    def _register_builtin_commands(self):
        """Register built-in command handlers."""
        self.register_command("status", self._handle_status_command)
        self.register_command("health", self._handle_health_command)
    
    async def _handle_status_command(self, parameters: dict[str, str]) -> dict[str, str]:
        """Built-in status command handler."""
        status = self.get_status()
        return {
            "command_type": "status",
            "running": str(status.running),
            "uptime_seconds": str(status.uptime_seconds),
            "total_runs": str(status.total_runs),
            "successful_runs": str(status.successful_runs),
            "failed_runs": str(status.failed_runs)
        }
    
    async def _handle_health_command(self, parameters: dict[str, str]) -> dict[str, str]:
        """Built-in health command handler."""
        return {
            "command_type": "health",
            "status": "healthy",
            "bridge_connected": str(self.websocket_client.connected if self.websocket_client else False)
        }
