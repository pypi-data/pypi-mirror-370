import os
import sys
from pathlib import Path
from datetime import datetime

_LOG_BASE: Path | None = None
_LOG_FILE: Path | None = None

def init_logger(base_path: str) -> None:
    """Initialize log directory once."""
    global _LOG_BASE, _LOG_FILE
    _LOG_BASE = Path(base_path)
    log_dir = _LOG_BASE / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    _LOG_FILE = log_dir / "log.log"

def log(msg: str, echo: bool = False) -> None:
    """Log with timestamp. Call `init_logger` once before using this."""
    if _LOG_FILE is None:
        raise RuntimeError("Logger not initialized. Call init_logger(path) first.")

    ts = datetime.now().strftime("%m/%d/%y %I:%M:%S%p")
    line = f"{ts} --- DEBUG --- {msg}\n"

    try:
        with _LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line)
        if echo:
            sys.stdout.write(line)
            sys.stdout.flush()
    except Exception as e:
        sys.stderr.write(f"[log_debug ERROR] {e}\n")
