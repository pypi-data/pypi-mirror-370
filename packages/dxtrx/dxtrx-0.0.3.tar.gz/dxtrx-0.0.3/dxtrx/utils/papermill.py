import sys
import os

import sys

def is_papermill_like():
    return any("--HistoryManager.hist_file=:memory:" in arg for arg in sys.argv)

def pm_exit(reason: str = "Notebook skipped.", exit_code: int = 0):
    print(f"✅ {reason}")
    if is_papermill_like():
        sys.exit(exit_code)
    else:
        print("ℹ️ Not running under Papermill/Dagstermill — skipping sys.exit to avoid traceback.")