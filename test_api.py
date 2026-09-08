import os
import sys

server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server")
sys.path.insert(0, server_dir)

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_api():
    print("Testing GET / (Static Web UI)...")
    res = client.get("/")
    assert res.status_code == 200
    assert "SynchroClip" in res.text
    print("UI served successfully!")

    print("Testing GET /api/sample-demo...")
    res = client.get("/api/sample-demo")
    assert res.status_code == 200
    demo_data = res.json()
    assert demo_data["status"] == "success"
    audio_id = demo_data["audio_id"]
    print(f"Demo loaded: audio_id={audio_id}, duration={demo_data['duration']}s")

    print("Testing GET /api/caption-templates...")
    tpl_res = client.get("/api/caption-templates")
    assert tpl_res.status_code == 200
    tpl_data = tpl_res.json()
    assert len(tpl_data["templates"]) >= 6
    assert "yellow" in tpl_data["colors"]
    print(f"Loaded {len(tpl_data['templates'])} caption templates.")

    print("Testing POST /api/generate-captions...")
    cap_res = client.post("/api/generate-captions", json={
        "audio_id": audio_id,
        "script_text": demo_data["script"],
        "template_id": "capcut_classic"
    })
    assert cap_res.status_code == 200
    cap_data = cap_res.json()
    assert len(cap_data["words"]) > 0
    assert len(cap_data["cards"]) > 0
    print(f"Aligned {len(cap_data['words'])} words into {len(cap_data['cards'])} caption cards.")

    print("Testing GET /api/download-project-zip...")
    zip_res = client.get("/api/download-project-zip")
    assert zip_res.status_code == 200
    assert len(zip_res.content) > 10000
    print(f"Project ZIP archive generated: {len(zip_res.content)} bytes.")

    print("Testing GET /api/git-info...")
    git_res = client.get("/api/git-info")
    assert git_res.status_code == 200
    assert len(git_res.json()["steps"]) > 0
    print("Git publishing instructions confirmed.")

    print("\nALL API ENDPOINTS TESTED & VERIFIED 100% OPERATIONAL! SUCCESS!")

if __name__ == "__main__":
    test_api()
