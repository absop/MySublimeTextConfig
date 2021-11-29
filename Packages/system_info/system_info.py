from .libs import psutil
from typing import List
import sublime
import time


class SystemInfo:
    def __init__(self, style: str = "%m/%d %H:%M:%S") -> None:
        self.style = style
        self.alive = True

    def stop(self) -> None:
        self.alive = False

    def tick(self) -> None:
        if not self.alive:
            self.update_status_msg("")
            return
        self.update_status_msg(self.generate_msg())
        sublime.set_timeout_async(self.tick, 1000)

    def generate_msg(self) -> str:
        msgs: List[str] = []
        msgs.append(f"⏰ {time.strftime(self.style)}")
        if battery := psutil.sensors_battery():
            percent = round(battery.percent)
            plugged = " +🔌" if battery.power_plugged else ""
            msgs.append(f"🔋 {percent}%{plugged}")
        return ", ".join(msgs)

    def update_status_msg(self, msg: str) -> None:
        for window in sublime.windows():
            if view := window.active_view():
                view.set_status("__system_info", msg)


system_info = SystemInfo()


def plugin_loaded() -> None:
    system_info.tick()


def plugin_unloaded() -> None:
    system_info.stop()
