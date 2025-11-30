import sys
from pathlib import Path
import os

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("ETHERSCAN_API_KEY", "test")
os.environ.setdefault("RATE_LIMIT", "5")
os.environ.setdefault("LOG_LEVEL", "INFO")

