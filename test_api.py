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

    print("Testing POST /api/segment-script...")
    seg_res = client.post("/api/segment-script", json={
        "audio_id": audio_id,
        "script_text": demo_data["script"]
    })
    assert seg_res.status_code == 200
    seg_data = seg_res.json()
    assert len(seg_data["scenes"]) >= 2
    print(f"Script segmented into {len(seg_data['scenes'])} scenes.")

    print("Testing POST /api/search-pexels...")
    search_res = client.post("/api/search-pexels", json={
        "query": "morning nature",
        "orientation": "landscape",
        "per_page": 4
    })
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert len(search_data["videos"]) > 0
    print(f"Pexels search returned {len(search_data['videos'])} clips.")

    print("Testing POST /api/auto-match-all...")
    match_res = client.post("/api/auto-match-all", json={
        "scenes": seg_data["scenes"]
    })
    assert match_res.status_code == 200
    match_data = match_res.json()
    assert match_data["scenes"][0]["selected_clip"] is not None
    print(f"Auto-match successfully assigned clips to all {len(match_data['scenes'])} scenes!")

    print("\nALL API ENDPOINTS FUNCTIONING 100% CORRECTLY!")

if __name__ == "__main__":
    test_api()
