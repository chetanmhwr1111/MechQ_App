import os
import sys
import threading
import time
import webbrowser
import streamlit.web.cli as stcli

# 1. Prevent crash on console=False (redirect None streams)
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://localhost:8501")

if __name__ == "__main__":
    # Resolve directory where PyInstaller extracted the files
    if getattr(sys, 'frozen', False):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    script_path = os.path.join(base_dir, "quiz_app.py")

    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    # Launch browser automatically once server starts
    threading.Thread(target=open_browser, daemon=True).start()

    sys.argv = [
        "streamlit",
        "run",
        script_path,
        "--global.developmentMode=false",
        "--server.headless=true",
    ]
    sys.exit(stcli.main())