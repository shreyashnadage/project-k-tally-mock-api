# Entry point when running as a packaged exe.
# - Sets DB path to %APPDATA%/TallySimulator/ so data survives upgrades
# - Starts uvicorn on 9001 (management UI), which spawns port 9000 (emulator)
# - Opens browser after a short delay

import os
import sys
import threading
import time
import webbrowser

# When frozen, ensure the bundled packages are importable
if getattr(sys, "frozen", False):
    app_data_dir = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "TallySimulator")
    os.makedirs(app_data_dir, exist_ok=True)
    os.environ.setdefault("DB_PATH", os.path.join(app_data_dir, "simulator.db"))

import uvicorn


def _open_browser():
    time.sleep(2.5)
    webbrowser.open("http://localhost:9001")


if __name__ == "__main__":
    print("=" * 60)
    print("  Tally Data Simulator")
    print("  Management UI  →  http://localhost:9001")
    print("  Tally Emulator →  http://localhost:9000")
    print("  Press Ctrl+C to stop")
    print("=" * 60)

    threading.Thread(target=_open_browser, daemon=True).start()

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=9001,
        log_level="info",
    )
