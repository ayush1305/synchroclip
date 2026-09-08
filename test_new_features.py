import os
import sys
import json
import subprocess
from fastapi.testclient import TestClient

server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server")
sys.path.insert(0, server_dir)

import caption_templates
import caption_generator
import video_composer
from app import app

client = TestClient(app)

def test_caption_templates_and_fonts():
    print("=== Test 1: Caption Templates (60+) & Famous Fonts ===")
    templates = caption_templates.TEMPLATES
    fonts = caption_templates.FAMOUS_FONTS
    colors = caption_templates.HIGHLIGHT_COLORS

    print(f"Total premade templates: {len(templates)}")
    print(f"Total famous fonts: {len(fonts)}")
    print(f"Total highlight colors: {len(colors)}")

    assert len(templates) >= 60, f"Expected at least 60 templates, got {len(templates)}"
    assert len(fonts) >= 10, f"Expected at least 10 fonts, got {len(fonts)}"
    assert "hormozi_classic" in templates
    assert "mrbeast_comic" in templates
    assert "neon_fox" in templates
    assert "slide_up_float" in templates
    assert "royal_gold" in templates

    header_montserrat = caption_templates.build_ass_header("hormozi_classic", 1920, 1080, font_override="Montserrat")
    assert "Montserrat" in header_montserrat
    print("Caption templates and font overrides verified!\n")

def test_api_caption_templates_endpoint():
    print("=== Test 2: GET /api/caption-templates Endpoint ===")
    resp = client.get("/api/caption-templates")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert len(data["templates"]) >= 60
    assert len(data["famous_fonts"]) >= 10
    assert "yellow" in data["colors"]
    print(f"API returned {len(data['templates'])} templates and {len(data['famous_fonts'])} fonts successfully!\n")

def test_video_upload_endpoint():
    print("=== Test 3: POST /api/upload-video Endpoint ===")
    test_video_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_user_clip.mp4")

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=purple:s=640x360:d=3",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        test_video_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    with open(test_video_path, "rb") as f:
        resp = client.post("/api/upload-video", files={"file": ("test_user_clip.mp4", f, "video/mp4")})

    assert resp.status_code == 200, f"Upload failed: {resp.text}"
    result = resp.json()
    assert result["status"] == "success"
    clip = result["clip"]
    assert clip["duration"] > 0
    assert clip["width"] == 640
    assert clip["height"] == 360
    assert clip["is_user_upload"] is True
    assert os.path.exists(clip["local_path"])
    print(f"Uploaded custom video successfully! ID: {clip['id']}, duration: {clip['duration']}s, path: {clip['local_path']}\n")

    if os.path.exists(test_video_path):
        os.remove(test_video_path)

    return clip

def test_full_render_with_custom_video_and_captions(custom_clip):
    print("=== Test 4: Full Multi-Clip Render with Custom Upload & Animated Captions ===")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    audio_path = os.path.join(base_dir, "test_full_audio.mp3")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=6",
        "-c:a", "libmp3lame",
        audio_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    stock_clip_path = os.path.join(base_dir, "test_stock_clip.mp4")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=teal:s=640x360:d=4",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        stock_clip_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    words = [
        {"word": "CREATE", "start": 0.5, "end": 1.5, "duration": 1.0},
        {"word": "AMAZING", "start": 1.5, "end": 3.0, "duration": 1.5},
        {"word": "VIRAL", "start": 3.0, "end": 4.5, "duration": 1.5},
        {"word": "CONTENT", "start": 4.5, "end": 6.0, "duration": 1.5}
    ]
    cards = caption_generator.chunk_words_into_cards(words, max_words_per_card=2)
    ass_path = os.path.join(base_dir, "test_render_subs.ass")

    caption_generator.generate_ass_subtitles(
        caption_cards=cards,
        template_id="hormozi_classic",
        highlight_color_key="#00ffcc",
        output_path=ass_path,
        width=1920,
        height=1080,
        font_family_override="Montserrat"
    )
    assert os.path.exists(ass_path)

    scenes = [
        {
            "id": 1,
            "duration": 3.0,
            "start_time": 0.0,
            "end_time": 3.0,
            "selected_clip": custom_clip
        },
        {
            "id": 2,
            "duration": 3.0,
            "start_time": 3.0,
            "end_time": 6.0,
            "selected_clip": {
                "id": "stock_1",
                "video_url": stock_clip_path,
                "local_path": stock_clip_path,
                "duration": 4.0
            }
        }
    ]

    job_id = "test_custom_render_job"
    video_composer.RENDER_JOBS[job_id] = {
        "id": job_id,
        "status": "queued",
        "progress": 0,
        "message": "Starting test render"
    }

    out_dir = os.path.join(base_dir, "output")
    cache_dir = os.path.join(base_dir, "cache")

    video_composer.render_video_task(
        job_id=job_id,
        scenes=scenes,
        audio_path=audio_path,
        total_audio_duration=6.0,
        transition_type="fade",
        transition_duration=0.5,
        aspect_ratio="16:9",
        caption_ass_path=ass_path,
        cache_dir=cache_dir,
        output_dir=out_dir
    )

    job_state = video_composer.RENDER_JOBS[job_id]
    assert job_state["status"] == "done", f"Render failed: {job_state.get('message')}"
    output_video_path = os.path.join(out_dir, job_state["output_file"])
    assert os.path.exists(output_video_path), "Final rendered MP4 was not created"
    assert os.path.getsize(output_video_path) > 1000, "Output MP4 is empty or corrupted"
    print(f"Final video rendered successfully: {output_video_path} ({os.path.getsize(output_video_path)} bytes)!\n")

    for f in [audio_path, stock_clip_path, ass_path, output_video_path]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass

if __name__ == "__main__":
    test_caption_templates_and_fonts()
    test_api_caption_templates_endpoint()
    uploaded_clip = test_video_upload_endpoint()
    test_full_render_with_custom_video_and_captions(uploaded_clip)
    print("======================================================")
    print("ALL 4 TEST SUITES PASSED! EVERYTHING WORKS FLAWLESSLY!")
    print("======================================================")
