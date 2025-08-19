import os
import time
import uuid

_forced_platform = None


def default_context():
    return {
        "trace_id": str(uuid.uuid4()),
        "timestamp": int(time.time()),
        "logger": None  # 可注入 get_logger("task-name")
    }


def set_forced_platform(name: str):
    global _forced_platform
    _forced_platform = name


def get_platform():
    return _forced_platform or os.environ.get("PLATFORM", "local")
