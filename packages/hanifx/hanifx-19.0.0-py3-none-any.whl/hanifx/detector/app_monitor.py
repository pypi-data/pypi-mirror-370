import subprocess
from .utils import load_previous_list, save_current_list, save_log

class AppMonitor:
    def __init__(self):
        pass

    def get_installed_apps(self):
        """ADB/Termux compatible installed apps fetch"""
        try:
            result = subprocess.check_output(["adb", "shell", "pm", "list", "packages", "-f"])
            apps = []
            for line in result.splitlines():
                line = line.decode().strip()
                if line.startswith("package:"):
                    parts = line.replace("package:", "").split("=")
                    if len(parts) == 2:
                        apk_path, pkg_name = parts
                        apps.append((pkg_name, apk_path))
            return apps
        except Exception as e:
            save_log(f"❌ Error fetching apps: {e}")
            return []

    def detect_new_apps(self):
        prev_apps = load_previous_list()
        curr_apps = self.get_installed_apps()

        prev_names = [x[0] for x in prev_apps]
        new_apps = [pkg for pkg in curr_apps if pkg[0] not in prev_names]

        if new_apps:
            for pkg_name, apk_path in new_apps:
                save_log(f"⚠️ New/Hidden App Detected: {pkg_name} (APK: {apk_path})")

        save_current_list(curr_apps)
        return new_apps
