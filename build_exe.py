import os
import sys
import subprocess

def build():
    print("Starting PyInstaller build for SynchroClip...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=SynchroClip",
        "--onedir",
        "--windowed",
        "--add-data=static;static",
        "--add-data=server;server",
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.loops",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=uvicorn.protocols",
        "--hidden-import=uvicorn.protocols.http",
        "--hidden-import=uvicorn.protocols.http.auto",
        "--hidden-import=uvicorn.protocols.websockets",
        "--hidden-import=uvicorn.protocols.websockets.auto",
        "--hidden-import=uvicorn.lifespan",
        "--hidden-import=uvicorn.lifespan.on",
        "--hidden-import=speech_recognition",
        "--hidden-import=requests",
        "--hidden-import=pydantic",
        "--noconfirm",
        "run.py"
    ]
    print("Running:", " ".join(cmd))
    res = subprocess.run(cmd)
    if res.returncode == 0:
        print("Build succeeded! Output in dist/SynchroClip/")
    else:
        print("Build failed with code:", res.returncode)

if __name__ == "__main__":
    build()
