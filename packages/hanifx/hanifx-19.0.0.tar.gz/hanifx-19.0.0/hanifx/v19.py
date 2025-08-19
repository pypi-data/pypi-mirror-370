from .detector.app_monitor import AppMonitor

class HanifX_v19:
    def __init__(self):
        self.monitor = AppMonitor()

    def run_scan(self):
        print("🔒 HanifX v19.0.0 Real-time App Guard Running...")
        new_apps = self.monitor.detect_new_apps()
        if new_apps:
            print("⚠️ Suspicious Apps Found:")
            for pkg_name, apk_path in new_apps:
                print("  →", pkg_name, "(APK:", apk_path, ")")
        else:
            print("✅ No new apps detected.")
