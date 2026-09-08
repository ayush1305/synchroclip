import os
import sys
import threading
import time
import webbrowser
import uvicorn

def open_browser(port):
    time.sleep(1.2)
    try:
        webbrowser.open(f"http://localhost:{port}")
    except Exception:
        pass

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        app_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))

    server_dir = os.path.join(app_dir, "server")
    if server_dir not in sys.path:
        sys.path.insert(0, server_dir)

    import app as server_app

    port = int(os.environ.get("PORT", 8080))
    print("=" * 60)
    print("  SynchroClip Studio - Standalone Desktop App")
    print(f"  Studio Web URL: http://localhost:{port}")
    print("  Opening browser automatically...")
    print("=" * 60)

    # Launch browser automatically for direct desktop app experience
    if os.environ.get("NO_BROWSER") != "1":
        threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    uvicorn.run(server_app.app, host="127.0.0.1", port=port, log_level="info")
