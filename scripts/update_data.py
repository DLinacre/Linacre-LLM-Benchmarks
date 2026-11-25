#!/usr/bin/env python3
"""Entry point for Linacre LLM Hub verified data refresh.

Replaces the legacy random-Elo script with the verified multi-source data engine.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_engine.run import run_all  # noqa: E402

if __name__ == "__main__":
    sys.exit(run_all())
