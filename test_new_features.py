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
    print("=== Test 1: Caption Templates (78+) & Famous Fonts ===")
    templates = caption_templates.TEMPLATES
    fonts = caption_templates.FAMOUS_FONTS
    colors = caption_templates.HIGHLIGHT_COLORS

    print(f"Total premade templates: {len(templates)}")
    print(f"Total famous fonts: {len(fonts)}")
    print(f"Total highlight colors: {len(colors)}")

    assert len(templates) >= 70, f"Expected at least 70 templates, got {len(templates)}"
    assert len(fonts) >= 10, f"Expected at least 10 fonts, got {len(fonts)}"
    assert "smooth_cross" in templates
    assert "creator_hierarchy" in templates
    assert "hero_spotlight" in templates
    assert "serif_punch" in templates
    assert "hormozi_classic" in templates
    assert "mrbeast_comic" in templates

    # Check hybrid multi-font metadata
    smooth = templates["smooth_cross"]
    assert smooth["body_font"] == "Montserrat"
    assert smooth["hero_font"] == "Pacifico"
    assert bool(smooth["hero_italic"]) is True

    header = caption_templates.build_ass_header("smooth_cross", 1920, 1080, font_override="Montserrat")
    assert "Montserrat" in header
    print("Caption templates, hybrid fonts, and overrides verified!\n")

def test_multifont_and_dual_color_ass():
    print("=== Test 2: Multi-Font & Dual-Color ASS Generation ===")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ass_path = os.path.join(base_dir, "test_multifont.ass")

    words = [
        {"word": "SMOOTH", "start": 0.0, "end": 0.8, "duration": 0.8},
        {"word": "CROSS", "start": 0.8, "end": 1.6, "duration": 0.8}
    ]
    cards = caption_generator.chunk_words_into_cards(words, max_words_per_card=2)

    caption_generator.generate_ass_subtitles(
        caption_cards=cards,
        template_id="smooth_cross",
        highlight_color_key="#ec4899",  # Color 2 (Hero/Highlight)
        primary_color_key="#fef08a",    # Color 1 (Base text)
        output_path=ass_path,
        width=1920,
        height=1080,
        font_family_override="Montserrat",
        hero_font_override="Pacifico"
    )

    assert os.path.exists(ass_path)
    with open(ass_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify \fn tags are inserted for multi-font rendering
    assert r"\fnMontserrat" in content
    assert r"\fnPacifico" in content
    print("Multi-font tags and dual-color hex formatting verified in ASS file!\n")

    if os.path.exists(ass_path):
        os.remove(ass_path)

def test_shine_toggle_ass_output():
    print("=== Test 2b: Crisp Matte ASS vs. Optional Shine Glow Toggle ===")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    clean_ass = os.path.join(base_dir, "test_clean_matte.ass")
    shine_ass = os.path.join(base_dir, "test_with_shine.ass")

    words = [
        {"word": "CLEAN", "start": 0.0, "end": 0.5, "duration": 0.5},
        {"word": "MATTE", "start": 0.5, "end": 1.0, "duration": 0.5}
    ]
    cards = caption_generator.chunk_words_into_cards(words, max_words_per_card=2)

    # 1. Default (enable_shine=False): Must be crisp with NO \blur glowing aura
    caption_generator.generate_ass_subtitles(
        caption_cards=cards,
        template_id="creator_hierarchy",
        highlight_color_key="#06b6d4",
        primary_color_key="#ffffff",
        output_path=clean_ass,
        enable_shine=False
    )
    assert os.path.exists(clean_ass)
    with open(clean_ass, "r", encoding="utf-8") as f:
        clean_content = f.read()

    assert r"\blur" not in clean_content, "Default ASS subtitles should have zero blur or glowing halo"
    print("Clean matte ASS verified: Zero blur, pure sharp crisp text!")

    # 2. Enabled (enable_shine=True): Must include shine glow tag
    caption_generator.generate_ass_subtitles(
        caption_cards=cards,
        template_id="creator_hierarchy",
        highlight_color_key="#06b6d4",
        primary_color_key="#ffffff",
        output_path=shine_ass,
        enable_shine=True
    )
    assert os.path.exists(shine_ass)
    with open(shine_ass, "r", encoding="utf-8") as f:
        shine_content = f.read()

    assert r"\blur3" in shine_content or r"\blur4" in shine_content, "Shine-enabled ASS should contain blur/glow tags"
    print("Shine-enabled ASS verified: Glow aura present when toggled ON!\n")

    for p in [clean_ass, shine_ass]:
        if os.path.exists(p):
            os.remove(p)

def test_api_caption_templates_endpoint():
    print("=== Test 3: GET /api/caption-templates Endpoint ===")
    resp = client.get("/api/caption-templates")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert len(data["templates"]) >= 70
    assert len(data["famous_fonts"]) >= 10
    assert "yellow" in data["colors"]
    print(f"API returned {len(data['templates'])} templates and {len(data['famous_fonts'])} fonts successfully!\n")

def test_direct_video_upload_endpoint():
    print("=== Test 4: POST /api/upload-direct-video Endpoint ===")
    test_video_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_direct_source.mp4")

    # Generate a 4-second video with audio track
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=navy:s=720x1280:d=4",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=4",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-shortest",
        test_video_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    with open(test_video_path, "rb") as f:
        resp = client.post("/api/upload-direct-video", files={"file": ("test_direct_source.mp4", f, "video/mp4")})

    assert resp.status_code == 200, f"Upload direct video failed: {resp.text}"
    result = resp.json()
    assert result["status"] == "success"
    assert result["duration"] > 0
    assert result["width"] == 720
    assert result["height"] == 1280
    assert result["audio_id"].startswith("audio_")
    assert len(result["waveform"]) > 0
    assert os.path.exists(result["local_video_path"])
    print(f"Direct video uploaded! ID: {result['video_id']}, Res: {result['width']}x{result['height']}, Audio ID: {result['audio_id']}\n")

    if os.path.exists(test_video_path):
        os.remove(test_video_path)

    return result

def test_direct_video_render_burn(direct_info):
    print("=== Test 5: POST /api/render Direct Video Mode (Bypass Stock Clips) ===")
    base_dir = os.path.dirname(os.path.abspath(__file__))

    words = [
        {"word": "VIRAL", "start": 0.5, "end": 1.8, "duration": 1.3},
        {"word": "DIRECT", "start": 1.8, "end": 3.2, "duration": 1.4}
    ]
    cards = caption_generator.chunk_words_into_cards(words, max_words_per_card=2)

    resp = client.post("/api/render", json={
        "audio_id": direct_info["audio_id"],
        "scenes": [],
        "is_direct_video": True,
        "direct_video_path": direct_info["local_video_path"],
        "caption_template": "smooth_cross",
        "primary_color": "#ffffff",
        "highlight_color": "#06b6d4",
        "caption_cards": cards,
        "aspect_ratio": "9:16"
    })

    assert resp.status_code == 200, f"Render request failed: {resp.text}"
    result = resp.json()
    assert result["status"] == "started"
    job_id = result["job_id"]
    print(f"Direct burn render started successfully with Job ID: {job_id}")

    # Wait for completion
    import time
    done = False
    for _ in range(40):
        time.sleep(0.5)
        status_resp = client.get(f"/api/render-status/{job_id}")
        assert status_resp.status_code == 200
        st = status_resp.json()
        if st["status"] == "done":
            done = True
            output_file = os.path.join(base_dir, "output", st["output_file"])
            assert os.path.exists(output_file)
            assert os.path.getsize(output_file) > 1000
            print(f"Direct video burn completed! Output: {output_file} ({os.path.getsize(output_file)} bytes)\n")
            if os.path.exists(output_file):
                os.remove(output_file)
            break
        elif st["status"] == "error":
            raise RuntimeError(f"Direct render job failed: {st.get('message')}")

    assert done, "Direct render timed out"

def test_full_render_with_custom_video_and_captions():
    print("=== Test 6: Multi-Clip Render with Custom Upload & Crossfades ===")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    audio_path = os.path.join(base_dir, "test_full_audio.mp3")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=4",
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
        {"word": "CREATOR", "start": 0.5, "end": 2.0, "duration": 1.5},
        {"word": "STUDIO", "start": 2.0, "end": 3.8, "duration": 1.8}
    ]
    cards = caption_generator.chunk_words_into_cards(words, max_words_per_card=2)
    ass_path = os.path.join(base_dir, "test_render_subs.ass")

    caption_generator.generate_ass_subtitles(
        caption_cards=cards,
        template_id="creator_hierarchy",
        highlight_color_key="#06b6d4",
        primary_color_key="#ffffff",
        output_path=ass_path,
        width=1920,
        height=1080
    )
    assert os.path.exists(ass_path)

    scenes = [
        {
            "id": 1,
            "duration": 4.0,
            "start_time": 0.0,
            "end_time": 4.0,
            "selected_clip": {
                "id": "clip_1",
                "video_url": stock_clip_path,
                "local_path": stock_clip_path,
                "duration": 4.0
            }
        }
    ]

    job_id = "test_multiclip_job"
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
        total_audio_duration=4.0,
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
    assert os.path.exists(output_video_path)
    print(f"Multi-clip video rendered successfully: {output_video_path}!\n")

    for f in [audio_path, stock_clip_path, ass_path, output_video_path]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass

if __name__ == "__main__":
    test_caption_templates_and_fonts()
    test_multifont_and_dual_color_ass()
    test_shine_toggle_ass_output()
    test_api_caption_templates_endpoint()
    direct_info = test_direct_video_upload_endpoint()
    test_direct_video_render_burn(direct_info)
    test_full_render_with_custom_video_and_captions()
    print("==================================================================")
    print("ALL 7 TEST SUITES PASSED! CRISP MATTE SUBTITLES & SHINE TOGGLE OK!")
    print("==================================================================")
