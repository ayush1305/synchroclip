import os
import sys
import uvicorn

if __name__ == "__main__":
    server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server")
    sys.path.insert(0, server_dir)

    port = int(os.environ.get("PORT", 8080))
    print("=" * 60)
    print("  SynchroClip - AI Audio-Synced Stock Video Studio")
    print(f"  Server running at: http://localhost:{port}")
    print("=" * 60)

    uvicorn.run("app:app", host="127.0.0.1", port=port, reload=False, app_dir=server_dir)
