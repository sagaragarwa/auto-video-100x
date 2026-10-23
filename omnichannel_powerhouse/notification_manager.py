"""
OmniChannel Notification Manager & WhatsApp-Style Event Bus
============================================================
Stores, manages, and delivers real-time notifications for video production,
unlisted uploads, and standing order executions.
"""

import os
import json
import time
import threading
from typing import Dict, Any, List, Optional

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTIFICATIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notifications.json")


class NotificationManager:
    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(NotificationManager, cls).__new__(cls)
                cls._instance._init_store()
            return cls._instance

    def _init_store(self):
        self.notifications: List[Dict[str, Any]] = []
        self.load_notifications()

    def load_notifications(self):
        with self._lock:
            if os.path.exists(NOTIFICATIONS_FILE):
                try:
                    with open(NOTIFICATIONS_FILE, "r", encoding="utf-8") as f:
                        self.notifications = json.load(f)
                except Exception:
                    self.notifications = []
            else:
                self.notifications = []

    def save_notifications(self):
        with self._lock:
            try:
                with open(NOTIFICATIONS_FILE, "w", encoding="utf-8") as f:
                    json.dump(self.notifications, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"[WARN] Could not save notifications: {e}")

    def add_notification(
        self,
        title: str,
        message: str,
        channel_key: str = "",
        channel_name: str = "",
        video_id: str = "",
        video_url: str = "",
        duration_min: float = 0.0,
        thumbnail_url: str = "",
        notif_type: str = "video_uploaded"
    ) -> Dict[str, Any]:
        """Creates and stores a new notification."""
        with self._lock:
            notif = {
                "id": f"notif_{int(time.time()*1000)}",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "type": notif_type,
                "title": title,
                "message": message,
                "channel_key": channel_key,
                "channel_name": channel_name or channel_key,
                "video_id": video_id,
                "video_url": video_url,
                "duration_min": duration_min,
                "thumbnail_url": thumbnail_url,
                "read": False
            }
            self.notifications.insert(0, notif)
            # Keep last 200 notifications
            if len(self.notifications) > 200:
                self.notifications = self.notifications[:200]
            self.save_notifications()
            return notif

    def get_all(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            return self.notifications[:limit]

    def get_unread(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [n for n in self.notifications if not n.get("read", False)]

    def mark_read(self, notif_id: str) -> bool:
        with self._lock:
            for n in self.notifications:
                if n.get("id") == notif_id:
                    n["read"] = True
                    self.save_notifications()
                    return True
            return False

    def mark_all_read(self) -> int:
        with self._lock:
            count = 0
            for n in self.notifications:
                if not n.get("read", False):
                    n["read"] = True
                    count += 1
            if count > 0:
                self.save_notifications()
            return count

    def clear_all(self) -> bool:
        with self._lock:
            self.notifications = []
            self.save_notifications()
            return True


NOTIFICATION_MANAGER = NotificationManager()


def post_video_ready_notification_to_chat(
    session_id: str,
    channel_name: str,
    title: str,
    duration_min: float,
    video_url: str,
    video_path: str = ""
):
    """
    Directly inserts an incoming notification message into the user's active chat session,
    creating a seamless WhatsApp-like incoming update!
    """
    from omnichannel_powerhouse.agent_commander.memory import save_message

    dur_str = f"{duration_min:.1f} Minutes" if duration_min else "N/A"
    formatted_msg = (
        f"🔔 **[LIVE UPDATE: Video Ready & Uploaded!]**\n\n"
        f"Aapki video safaltapoorvak manufacture hokar **{channel_name}** par upload ho chuki hai!\n\n"
        f"• **Title:** {title}\n"
        f"• **Channel:** `{channel_name}`\n"
        f"• **Duration:** {dur_str}\n"
        f"• **Staging:** Unlisted (Review Ready)\n"
    )
    if video_url:
        formatted_msg += f"• **Watch Link:** [{video_url}]({video_url})\n"
    if video_path:
        clean_p = video_path.replace("\\", "/")
        formatted_msg += f"• **Local File:** [`{os.path.basename(video_path)}`](file:///{clean_p})\n"

    formatted_msg += "\n*Chatbot ne notification store me save kar di hai aur standing orders active hain.*"

    save_message(
        session_id=session_id,
        role="assistant",
        content=formatted_msg,
        thinking=f"Notification delivered for completed video on {channel_name}."
    )
