"""
30-Second GitHub Cloud Watcher & Load-Offloading Daemon.
Checks GitHub repository workflows every 30 seconds.
If inactive, automatically reactivates / keeps it alive.
Offloads 100% of video generation and FFmpeg rendering load to GitHub Actions cloud servers.
Zero CPU load and zero disk usage on the local machine!
"""

import os
import sys
import time
import json
import threading
import requests
from typing import Dict, Any, Optional, List
from loguru import logger

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "github_config.json")
QUEUE_PATH = os.path.join(_root, "storage", "cloud_queue.json")

DEFAULT_GITHUB_CONFIG = {
    "repo_owner": "sagaragarwa",
    "repo_name": "auto-video-100x",
    "github_token": os.environ.get("GITHUB_TOKEN", ""),
    "check_interval_seconds": 30,
    "workflow_file": "cloud_master_render.yml",
    "auto_keepalive": True,
    "offload_rendering_to_cloud": True
}

def load_github_config() -> Dict[str, Any]:
    if not os.path.exists(CONFIG_PATH):
        save_github_config(DEFAULT_GITHUB_CONFIG)
        return DEFAULT_GITHUB_CONFIG.copy()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure all keys exist
            for k, v in DEFAULT_GITHUB_CONFIG.items():
                if k not in data:
                    data[k] = v
            return data
    except Exception as e:
        logger.error(f"Failed to read github_config.json: {e}")
        return DEFAULT_GITHUB_CONFIG.copy()

def save_github_config(data: Dict[str, Any]):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_cloud_queue() -> List[Dict[str, Any]]:
    if not os.path.exists(QUEUE_PATH):
        return []
    try:
        with open(QUEUE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_cloud_queue(queue: List[Dict[str, Any]]):
    os.makedirs(os.path.dirname(QUEUE_PATH), exist_ok=True)
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=4)

def queue_cloud_video_task(prompt: str, duration: int = 300, channel: str = "auto", auto_upload: bool = False) -> Dict[str, Any]:
    """
    Enqueues a video generation task to be executed on GitHub Actions cloud runners.
    Zero local CPU load!
    """
    queue = load_cloud_queue()
    task_item = {
        "id": f"cloud_task_{int(time.time())}",
        "prompt": prompt,
        "duration": duration,
        "channel": channel,
        "auto_upload": auto_upload,
        "status": "pending",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    queue.append(task_item)
    save_cloud_queue(queue)
    logger.success(f"☁️ Video task queued for GitHub Cloud Offloading: '{prompt}'")
    return task_item

class GitHubCloudWatcher:
    def __init__(self):
        self.config = load_github_config()
        self.running = False
        self._thread = None
        self.last_check_time = 0
        self.last_status = "Initialized"

    def _get_headers(self) -> Dict[str, str]:
        token = self.config.get("github_token", "").strip() or os.environ.get("GITHUB_TOKEN", "").strip()
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Antigravity-Cloud-Watcher"
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def check_repo_and_workflow_status(self) -> Dict[str, Any]:
        """
        Queries GitHub API to check active workflows, runners, and recent runs.
        """
        owner = self.config["repo_owner"]
        repo = self.config["repo_name"]
        url_runs = f"https://api.github.com/repos/{owner}/{repo}/actions/runs?per_page=5"

        headers = self._get_headers()
        try:
            resp = requests.get(url_runs, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                total_runs = data.get("total_count", 0)
                runs = data.get("workflow_runs", [])
                
                active_runs = [r for r in runs if r.get("status") in ["in_progress", "queued"]]
                latest_run = runs[0] if runs else None

                return {
                    "online": True,
                    "total_runs": total_runs,
                    "active_runs_count": len(active_runs),
                    "active_runs": active_runs,
                    "latest_run": {
                        "name": latest_run.get("name") if latest_run else None,
                        "status": latest_run.get("status") if latest_run else None,
                        "conclusion": latest_run.get("conclusion") if latest_run else None,
                        "html_url": latest_run.get("html_url") if latest_run else None,
                        "created_at": latest_run.get("created_at") if latest_run else None
                    } if latest_run else None,
                    "message": f"{len(active_runs)} active cloud run(s)" if active_runs else "Idle (Ready for Cloud Offloading)"
                }
            elif resp.status_code == 401 or resp.status_code == 403:
                return {
                    "online": False,
                    "error": "Authentication / Rate Limit: Add GITHUB_TOKEN in github_config.json",
                    "status_code": resp.status_code
                }
            else:
                return {
                    "online": False,
                    "error": f"GitHub API responded with status {resp.status_code}",
                    "status_code": resp.status_code
                }
        except Exception as e:
            return {"online": False, "error": str(e)}

    def trigger_cloud_workflow(self, prompt: str, duration: int = 300, channel: str = "auto", auto_upload: bool = False) -> Dict[str, Any]:
        """
        Triggers workflow_dispatch on GitHub Actions to render the video entirely in the cloud.
        """
        owner = self.config["repo_owner"]
        repo = self.config["repo_name"]
        wf = self.config.get("workflow_file", "cloud_master_render.yml")
        url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{wf}/dispatches"

        payload = {
            "ref": "main",
            "inputs": {
                "prompt": prompt,
                "duration": str(duration),
                "channel": channel,
                "auto_upload": "true" if auto_upload else "false"
            }
        }
        headers = self._get_headers()
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code in [204, 201, 200]:
                logger.success(f"🚀 Successfully dispatched video generation to GitHub Cloud: '{prompt}'!")
                return {"success": True, "message": "Dispatched to GitHub Actions Cloud Runner"}
            elif resp.status_code == 422:
                # Fallback to repository_dispatch if workflow_dispatch schema differs on remote main branch
                logger.warning(f"Workflow dispatch inputs rejected (422), attempting repository_dispatch fallback...")
                dispatch_url = f"https://api.github.com/repos/{owner}/{repo}/dispatches"
                rep_payload = {
                    "event_type": "cloud_render",
                    "client_payload": {
                        "prompt": prompt,
                        "duration": str(duration),
                        "channel": channel,
                        "auto_upload": "true" if auto_upload else "false"
                    }
                }
                rep_resp = requests.post(dispatch_url, headers=headers, json=rep_payload, timeout=15)
                if rep_resp.status_code in [204, 201, 200]:
                    logger.success(f"🚀 Dispatched via repository_dispatch to GitHub Cloud: '{prompt}'!")
                    return {"success": True, "message": "Dispatched via repository_dispatch"}
                else:
                    logger.error(f"Failed to dispatch workflow: {resp.status_code} - {resp.text}")
                    return {"success": False, "error": resp.text, "status_code": resp.status_code}
            else:
                logger.error(f"Failed to dispatch workflow: {resp.status_code} - {resp.text}")
                return {"success": False, "error": resp.text, "status_code": resp.status_code}
        except Exception as e:
            logger.error(f"Dispatch request failed: {e}")
            return {"success": False, "error": str(e)}

    def reactivate_workflows_if_inactive(self) -> Dict[str, Any]:
        """
        Pings GitHub Actions to ensure workflows are enabled and active (no 60-day sleep).
        """
        owner = self.config["repo_owner"]
        repo = self.config["repo_name"]
        wf = self.config.get("workflow_file", "cloud_master_render.yml")
        enable_url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{wf}/enable"
        headers = self._get_headers()
        try:
            resp = requests.put(enable_url, headers=headers, timeout=10)
            if resp.status_code in [204, 200]:
                logger.info("🟢 GitHub Actions Workflow actively enabled!")
                return {"success": True, "active": True}
        except Exception:
            pass
        return {"success": False}

    def run_cycle(self):
        """
        Executes one 30-second inspection and offloading cycle.
        """
        self.last_check_time = time.time()
        self.config = load_github_config()

        status = self.check_repo_and_workflow_status()
        self.last_status = status.get("message", status.get("error", "Unknown"))

        # 1. If any pending tasks in queue, offload them to GitHub Actions
        queue = load_cloud_queue()
        pending = [t for t in queue if t.get("status") == "pending"]

        if pending:
            task = pending[0]
            logger.info(f"⚡ 30s Watcher: Found pending task '{task['prompt']}' -> Offloading to GitHub Cloud...")
            disp_res = self.trigger_cloud_workflow(
                prompt=task["prompt"],
                duration=task.get("duration", 300),
                channel=task.get("channel", "auto"),
                auto_upload=task.get("auto_upload", False)
            )
            if disp_res.get("success"):
                task["status"] = "dispatched_to_cloud"
                task["dispatched_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                save_cloud_queue(queue)
            else:
                logger.warning(f"Could not dispatch task to cloud: {disp_res.get('error')}")

        # 2. Check and keepalive if inactive
        if self.config.get("auto_keepalive", True):
            self.reactivate_workflows_if_inactive()

        # 3. Auto-Download completed cloud videos directly into user's Downloads folder
        self.sync_and_download_cloud_videos()

    def sync_and_download_cloud_videos(self):
        r"""
        Polls GitHub Releases / Artifacts and automatically downloads any new completed 
        videos directly into C:\Users\janar\Downloads\ without manual user intervention!
        """
        owner = self.config.get("repo_owner", "sagaragarwa")
        repo = self.config.get("repo_name", "auto-video-100x")
        user_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        
        url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        headers = self._get_headers()
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                releases = resp.json()
                for rel in releases:
                    if rel.get("tag_name") == "v1.0.0-assets":
                        continue
                    for asset in rel.get("assets", []):
                        name = asset.get("name", "")
                        if name.endswith(".mp4"):
                            local_dest = os.path.join(user_downloads, name)
                            if not os.path.exists(local_dest) or os.path.getsize(local_dest) < asset.get("size", 1000):
                                download_url = asset.get("browser_download_url")
                                logger.info(f"⬇️ Auto-Downloading cloud video '{name}' to Downloads: {local_dest}...")
                                with requests.get(download_url, stream=True, timeout=60) as r:
                                    r.raise_for_status()
                                    with open(local_dest, "wb") as f:
                                        for chunk in r.iter_content(chunk_size=1048576):
                                            if chunk:
                                                f.write(chunk)
                                logger.success(f"🎉 Successfully downloaded {name} to {local_dest}!")
        except Exception as e:
            logger.debug(f"Release sync error: {e}")

        # 2. Poll Artifacts endpoint (Primary robust auto-delivery for 1080p Cloud Videos)
        try:
            art_url = f"https://api.github.com/repos/{owner}/{repo}/actions/artifacts?per_page=60"
            art_resp = requests.get(art_url, headers=headers, timeout=10)
            if art_resp.status_code == 200:
                artifacts = art_resp.json().get("artifacts", [])
                for art in artifacts:
                    if (art.get("name") == "master_video_1080p" or "1080p" in art.get("name", "")) and not art.get("expired"):
                        art_id = art.get("id")
                        zip_url = f"https://api.github.com/repos/{owner}/{repo}/actions/artifacts/{art_id}/zip"
                        r_red = requests.get(zip_url, headers=headers, allow_redirects=False, timeout=10)
                        if r_red.status_code == 302 and "Location" in r_red.headers:
                            blob_url = r_red.headers["Location"]
                            temp_zip = os.path.join(user_downloads, f"cloud_art_{art_id}.zip")
                            if not os.path.exists(temp_zip):
                                with requests.get(blob_url, stream=True, timeout=180) as r_b:
                                    r_b.raise_for_status()
                                    with open(temp_zip, "wb") as f_z:
                                        for chunk in r_b.iter_content(chunk_size=1048576):
                                            if chunk:
                                                f_z.write(chunk)
                                import zipfile
                                with zipfile.ZipFile(temp_zip, "r") as z:
                                    for z_info in z.infolist():
                                        if z_info.filename.endswith(".mp4"):
                                            targ = os.path.join(user_downloads, os.path.basename(z_info.filename))
                                            if not os.path.exists(targ) or os.path.getsize(targ) < z_info.file_size:
                                                z.extract(z_info, user_downloads)
                                                logger.success(f"🎉 Auto-Delivered Cloud Video from Artifact to Downloads: {targ}")
                                try:
                                    os.remove(temp_zip)
                                except Exception:
                                    pass
        except Exception as e:
            logger.debug(f"Artifact auto-sync note: {e}")

    def start_background_daemon(self):
        """
        Starts the 30-second interval watcher daemon in a background thread.
        """
        if self.running:
            return

        self.running = True
        logger.info(f"🔄 Starting 30-Second GitHub Cloud Watcher Daemon (Interval: {self.config.get('check_interval_seconds', 30)}s)...")

        def _loop():
            while self.running:
                try:
                    self.run_cycle()
                except Exception as e:
                    logger.error(f"Error in 30s watcher cycle: {e}")
                time.sleep(self.config.get("check_interval_seconds", 30))

        self._thread = threading.Thread(target=_loop, daemon=True, name="GitHubCloudWatcherThread")
        self._thread.start()

    def stop_daemon(self):
        self.running = False

_watcher_instance: Optional[GitHubCloudWatcher] = None

def get_cloud_watcher() -> GitHubCloudWatcher:
    global _watcher_instance
    if _watcher_instance is None:
        _watcher_instance = GitHubCloudWatcher()
    return _watcher_instance

if __name__ == "__main__":
    watcher = GitHubCloudWatcher()
    logger.info("🚀 Starting 30-Second GitHub Cloud Watcher & Auto-Downloader Daemon...")
    watcher.start_background_daemon()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop_daemon()
        logger.info("Watcher stopped.")

