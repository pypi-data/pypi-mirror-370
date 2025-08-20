"""
Profile Manager - Browser profile lifecycle management
Layer 2: Profile management with proxy binding inspired by unrealparser
"""

import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import logging
from unrealon_browser.dto import ProfileType, ProxyInfo

logger = logging.getLogger(__name__)


class ProfileManager:
    """
    Browser profile lifecycle management with proxy binding

    Layer 2: Profile management capabilities
    - Proxy-based profile generation
    - Profile metadata tracking
    - Automatic cleanup policies
    - Profile health monitoring
    """

    def __init__(self, profiles_dir: str = "./browser_profiles", logger_bridge=None):
        """Initialize profile manager"""
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.logger_bridge = logger_bridge

        # Initialize metadata database
        self.db_path = self.profiles_dir / "profiles_metadata.db"
        self._init_metadata_db()

        self.current_profile_path: Optional[Path] = None
        self.current_profile_type: Optional[ProfileType] = None
        self.current_proxy_info: Optional[ProxyInfo] = None

        self._logger(f"📁 Profile manager initialized: {self.profiles_dir}", "info")

    def _logger(self, message: str, level: str = "info") -> None:
        if self.logger_bridge:
            if level == "info":
                self.logger_bridge.log_info(message)
            elif level == "error":
                self.logger_bridge.log_error(message)
            elif level == "warning":
                self.logger_bridge.log_warning(message)
            else:
                self.logger_bridge.log_info(message)
        else:
            if level == "info":
                logger.info(message)
            elif level == "error":
                logger.error(message)
            elif level == "warning":
                logger.warning(message)
            else:
                logger.info(message)

    def _init_metadata_db(self) -> None:
        """Initialize SQLite metadata database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS profiles (
                        profile_name TEXT PRIMARY KEY,
                        profile_type TEXT NOT NULL,
                        proxy_host TEXT,
                        proxy_port INTEGER,
                        proxy_username TEXT,
                        proxy_password TEXT,
                        proxy_ip TEXT,
                        created_at TEXT NOT NULL,
                        last_used_at TEXT,
                        size_bytes INTEGER DEFAULT 0,
                        session_count INTEGER DEFAULT 0,
                        success_count INTEGER DEFAULT 0,
                        failure_count INTEGER DEFAULT 0,
                        metadata_json TEXT
                    )
                """
                )
                conn.commit()
            self._logger(" ✅ Profile metadata database initialized", "info")
        except Exception as e:
            self._logger(f"❌ Failed to initialize metadata database: {e}", "error")

    def _generate_profile_name(self, parser_name: str, proxy_info: Optional[ProxyInfo] = None) -> str:
        """Generate profile name based on parser and proxy"""
        if proxy_info:
            # Proxy-bound profile name
            return f"{parser_name}_proxy_{proxy_info.host}_{proxy_info.port}"
        else:
            # Direct connection profile name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"{parser_name}_direct_{timestamp}"

    def create_profile(self, parser_name: str, proxy_info: Optional[ProxyInfo] = None, profile_type: ProfileType = ProfileType.PROXY_BOUND) -> Path:
        """
        Create browser profile directory
        Inspired by unrealparser's profile creation strategy
        """
        try:
            # Generate profile name
            profile_name = self._generate_profile_name(parser_name, proxy_info)
            profile_path = self.profiles_dir / profile_name

            self._logger(f"📁 Creating profile: {profile_name}", "info")
            self._logger(f"   Type: {profile_type.value}", "info")
            if proxy_info:
                self._logger(f"   Proxy: {proxy_info.host}:{proxy_info.port}", "info")

            # Create profile directory
            profile_path.mkdir(parents=True, exist_ok=True)

            self._logger(f"   📂 Profile directory created:", "info")
            self._logger(f"    Path: {profile_path}", "info")
            self._logger(f"    Absolute: {profile_path.resolve()}", "info")
            self._logger(f"    Exists: {profile_path.exists()}", "info")
            self._logger(f"    Is directory: {profile_path.is_dir()}", "info")

            # Store current profile info
            self.current_profile_path = profile_path
            self.current_profile_type = profile_type
            self.current_proxy_info = proxy_info

            # Save profile metadata to database
            self._save_profile_metadata(profile_name=profile_name, profile_type=profile_type, proxy_info=proxy_info, profile_path=profile_path)

            self._logger(f"   ✅ Profile created: {profile_path}", "info")
            return profile_path

        except Exception as e:
            self._logger(f"❌ Failed to create profile: {e}", "error")
            raise

    def _save_profile_metadata(self, profile_name: str, profile_type: ProfileType, proxy_info: Optional[ProxyInfo], profile_path: Path) -> None:
        """Save profile metadata to database"""
        try:
            # Calculate profile size
            size_bytes = self._calculate_profile_size(profile_path)

            # Prepare metadata
            metadata = {
                "profile_path": str(profile_path),
                "parser_name": profile_name.split("_")[0],
                "created_timestamp": datetime.now(timezone.utc).isoformat(),
            }

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO profiles (
                        profile_name, profile_type, proxy_host, proxy_port,
                        proxy_username, proxy_password, proxy_ip,
                        created_at, last_used_at, size_bytes, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        profile_name,
                        profile_type.value,
                        proxy_info.host if proxy_info else None,
                        proxy_info.port if proxy_info else None,
                        proxy_info.username if proxy_info else None,
                        proxy_info.password if proxy_info else None,
                        proxy_info.ip if proxy_info else None,
                        datetime.now(timezone.utc).isoformat(),
                        datetime.now(timezone.utc).isoformat(),
                        size_bytes,
                        json.dumps(metadata),
                    ),
                )
                conn.commit()

        except Exception as e:
            self._logger(f"❌ Failed to save profile metadata: {e}", "error")

    def _calculate_profile_size(self, profile_path: Path) -> int:
        """Calculate total size of profile directory"""
        try:
            if not profile_path.exists():
                return 0

            total_size = 0
            for file_path in profile_path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return total_size

        except Exception as e:
            self._logger(f"⚠️ Failed to calculate profile size: {e}", "warning")
            return 0

    def get_profile_for_proxy(self, parser_name: str, proxy_info: ProxyInfo) -> Optional[Path]:
        """Get existing profile for specific proxy"""
        try:
            profile_name = self._generate_profile_name(parser_name, proxy_info)
            profile_path = self.profiles_dir / profile_name

            if profile_path.exists():
                self._logger(f"📁 Found existing profile: {profile_name}", "info")

                # Update last used timestamp
                self._update_profile_usage(profile_name)

                # Store current profile info
                self.current_profile_path = profile_path
                self.current_profile_type = ProfileType.PROXY_BOUND
                self.current_proxy_info = proxy_info

                return profile_path

            return None

        except Exception as e:
            self._logger(f"❌ Failed to get profile for proxy: {e}", "error")
            return None

    def _update_profile_usage(self, profile_name: str) -> None:
        """Update profile usage statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE profiles 
                    SET last_used_at = ?, session_count = session_count + 1
                    WHERE profile_name = ?
                """,
                    (datetime.now(timezone.utc).isoformat(), profile_name),
                )
                conn.commit()

        except Exception as e:
            self._logger(f"⚠️ Failed to update profile usage: {e}", "warning")

    def mark_session_success(self, success: bool = True) -> None:
        """Mark current session as success or failure"""
        if not self.current_profile_path:
            return

        try:
            profile_name = self.current_profile_path.name

            with sqlite3.connect(self.db_path) as conn:
                if success:
                    conn.execute(
                        """
                        UPDATE profiles 
                        SET success_count = success_count + 1
                        WHERE profile_name = ?
                    """,
                        (profile_name,),
                    )
                else:
                    conn.execute(
                        """
                        UPDATE profiles 
                        SET failure_count = failure_count + 1
                        WHERE profile_name = ?
                    """,
                        (profile_name,),
                    )
                conn.commit()

        except Exception as e:
            self._logger(f"⚠️ Failed to mark session result: {e}", "warning")

    def list_profiles(self, parser_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all profiles with metadata"""
        try:
            query = "SELECT * FROM profiles"
            params = []

            if parser_name:
                query += " WHERE profile_name LIKE ?"
                params.append(f"{parser_name}_%")

            query += " ORDER BY last_used_at DESC"

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)
                profiles = []

                for row in cursor.fetchall():
                    profile_data = dict(row)

                    # Add calculated fields
                    profile_path = Path(profile_data["profile_name"])
                    profile_data["exists"] = (self.profiles_dir / profile_path).exists()
                    profile_data["size_mb"] = profile_data["size_bytes"] / (1024 * 1024) if profile_data["size_bytes"] else 0

                    # Calculate success rate
                    total_sessions = profile_data["session_count"] or 0
                    if total_sessions > 0:
                        success_rate = (profile_data["success_count"] or 0) / total_sessions
                        profile_data["success_rate"] = success_rate
                    else:
                        profile_data["success_rate"] = 0.0

                    profiles.append(profile_data)

                return profiles

        except Exception as e:
            self._logger(f"❌ Failed to list profiles: {e}", "error")
            return []

    def cleanup_old_profiles(self, max_age_days: int = 30, max_size_mb: int = 1000) -> int:
        """
        Cleanup old or oversized profiles
        Inspired by unrealparser's cleanup strategy
        """
        try:
            self._logger(f"🧹 Cleaning up profiles older than {max_age_days} days or larger than {max_size_mb}MB", "info")

            cutoff_date = datetime.now(timezone.utc).timestamp() - (max_age_days * 24 * 3600)
            cleaned_count = 0

            profiles = self.list_profiles()

            for profile in profiles:
                should_delete = False
                reason = ""

                # Check age
                if profile["created_at"]:
                    created_timestamp = datetime.fromisoformat(profile["created_at"].replace("Z", "+00:00")).timestamp()
                    if created_timestamp < cutoff_date:
                        should_delete = True
                        reason = f"older than {max_age_days} days"

                # Check size
                if profile["size_mb"] > max_size_mb:
                    should_delete = True
                    reason = f"larger than {max_size_mb}MB ({profile['size_mb']:.1f}MB)"

                if should_delete and profile["exists"]:
                    profile_path = self.profiles_dir / profile["profile_name"]
                    try:
                        shutil.rmtree(profile_path)
                        self._logger(f"   🗑️ Deleted profile {profile['profile_name']} ({reason})", "info")
                        cleaned_count += 1

                        # Remove from database
                        with sqlite3.connect(self.db_path) as conn:
                            conn.execute("DELETE FROM profiles WHERE profile_name = ?", (profile["profile_name"],))
                            conn.commit()

                    except Exception as e:
                        self._logger(f"   ❌ Failed to delete profile {profile['profile_name']}: {e}", "error")

            self._logger(f"✅ Cleanup completed: {cleaned_count} profiles removed", "info")
            return cleaned_count

        except Exception as e:
            self._logger(f"❌ Profile cleanup failed: {e}", "error")
            return 0

    def get_profile_statistics(self) -> Dict[str, Any]:
        """Get overall profile statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Basic counts
                cursor = conn.execute("SELECT COUNT(*) as total_profiles FROM profiles")
                total_profiles = cursor.fetchone()["total_profiles"]

                # Profile types
                cursor = conn.execute(
                    """
                    SELECT profile_type, COUNT(*) as count 
                    FROM profiles 
                    GROUP BY profile_type
                """
                )
                profile_types = {row["profile_type"]: row["count"] for row in cursor.fetchall()}

                # Size statistics
                cursor = conn.execute(
                    """
                    SELECT 
                        SUM(size_bytes) as total_size,
                        AVG(size_bytes) as avg_size,
                        MAX(size_bytes) as max_size
                    FROM profiles
                """
                )
                size_stats = cursor.fetchone()

                # Session statistics
                cursor = conn.execute(
                    """
                    SELECT 
                        SUM(session_count) as total_sessions,
                        SUM(success_count) as total_successes,
                        SUM(failure_count) as total_failures
                    FROM profiles
                """
                )
                session_stats = cursor.fetchone()

                return {
                    "total_profiles": total_profiles,
                    "profile_types": profile_types,
                    "total_size_mb": (size_stats["total_size"] or 0) / (1024 * 1024),
                    "avg_size_mb": (size_stats["avg_size"] or 0) / (1024 * 1024),
                    "max_size_mb": (size_stats["max_size"] or 0) / (1024 * 1024),
                    "total_sessions": session_stats["total_sessions"] or 0,
                    "total_successes": session_stats["total_successes"] or 0,
                    "total_failures": session_stats["total_failures"] or 0,
                    "overall_success_rate": ((session_stats["total_successes"] or 0) / (session_stats["total_sessions"] or 1) if session_stats["total_sessions"] else 0.0),
                }

        except Exception as e:
            self._logger(f"❌ Failed to get profile statistics: {e}", "error")
            return {}

    def print_profile_statistics(self) -> None:
        """Print profile statistics"""
        stats = self.get_profile_statistics()

        print("\n📁 Profile Manager Statistics:")
        print(f"   Total profiles: {stats.get('total_profiles', 0)}")
        print(f"   Total size: {stats.get('total_size_mb', 0):.1f}MB")
        print(f"   Average size: {stats.get('avg_size_mb', 0):.1f}MB")
        print(f"   Total sessions: {stats.get('total_sessions', 0)}")
        print(f"   Success rate: {stats.get('overall_success_rate', 0):.1%}")

        profile_types = stats.get("profile_types", {})
        if profile_types:
            if self.logger_bridge:
                self.logger_bridge.log_info("   Profile types:")
                for ptype, count in profile_types.items():
                    self.logger_bridge.log_info(f"     {ptype}: {count}")

    def get_current_profile_info(self) -> Optional[Dict[str, Any]]:
        """Get information about current active profile"""
        if not self.current_profile_path:
            return None

        return {
            "profile_path": str(self.current_profile_path),
            "profile_name": self.current_profile_path.name,
            "profile_type": self.current_profile_type.value if self.current_profile_type else None,
            "proxy_info": (
                {
                    "host": self.current_proxy_info.host,
                    "port": self.current_proxy_info.port,
                    "ip": self.current_proxy_info.ip,
                }
                if self.current_proxy_info
                else None
            ),
            "exists": self.current_profile_path.exists(),
            "size_mb": self._calculate_profile_size(self.current_profile_path) / (1024 * 1024),
        }
