"""
Daemon Manager - Base class for parser daemons

Strict Pydantic v2 compliance and type safety
"""

import asyncio
import signal
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from .parser_manager import ParserManager, ParserManagerConfig
from .managers import ParserConfig, LoggingConfig, HTMLCleaningConfig, BrowserConfig

# RPC removed - all commands go through WebSocket bridge


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
        
        # RPC removed - commands come through WebSocket bridge
    
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
            
            # RPC server removed - using WebSocket bridge
            
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
        print(f"{status} | 💾 System: {self.config.system_dir}")
    
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
            failed_runs=self.failed_runs
        )
    
    async def cleanup(self):
        """Cleanup daemon resources."""
        # RPC server removed - only parent cleanup needed
        await super().cleanup()
