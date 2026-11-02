"""Offline-safe helpers: importing this module never contacts a guest."""
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path


def utc():
    return datetime.now(timezone.utc).isoformat(timespec='microseconds')


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def guestops(path):
    spec = importlib.util.spec_from_file_location('adlab_guestops', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
