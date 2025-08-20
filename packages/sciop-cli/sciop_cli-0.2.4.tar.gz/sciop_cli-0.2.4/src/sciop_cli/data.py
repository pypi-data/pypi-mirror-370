"""
Data that is used by sciop-cli that may need to be downloaded before being used
"""

from pathlib import Path

import requests
from platformdirs import PlatformDirs

_dirs = PlatformDirs("sciop-cli", "sciop")

DATA_DIR = Path(_dirs.user_data_dir)
DEFAULT_TRACKERS = DATA_DIR / "trackers.txt"
DEFAULT_TRACKER_SOURCE = "https://sciop.net/docs/uploading/default_trackers.txt"


def get_default_trackers(tracker_source: str = DEFAULT_TRACKER_SOURCE) -> list[str]:
    if not DEFAULT_TRACKERS.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        res = requests.get(tracker_source)
        res.raise_for_status()
        with open(DEFAULT_TRACKERS, "w") as f:
            f.write(res.text)
        trackers = res.text.splitlines()
    else:
        trackers = DEFAULT_TRACKERS.read_text().splitlines()
    trackers = [t.strip() for t in trackers if t.strip()]
    return trackers
