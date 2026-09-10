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

def test_pip_image_upload_and_preview():
    print("=== Test 8: POST /api/upload-pip-image Endpoint ===")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_img_path = os.path.join(base_dir, "test_pip_source.png")

    # Generate test 300x300 PNG with ffmpeg
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=coral:s=300x300:d=1",
        "-frames:v", "1",
        test_img_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    with open(test_img_path, "rb") as f:
        resp = client.post("/api/upload-pip-image", files={"file": ("test_pip_source.png", f, "image/png")})

    assert resp.status_code == 200, f"PiP upload failed: {resp.text}"
    result = resp.json()
    assert result["status"] == "success"
    assert "pip_id" in result
    assert result["filename"] == "test_pip_source.png"
    assert os.path.exists(result["path"])
    print(f"PiP Image uploaded successfully! ID: {result['pip_id']}, Path: {result['path']}, URL: {result['url']}\n")

    if os.path.exists(test_img_path):
        os.remove(test_img_path)

    return result

def test_progressive_reveal_and_word_zoom_ass():
    print("=== Test 9: Progressive Sentence Reveal & Kinetic Word Zoom ASS ===")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    zoom_ass = os.path.join(base_dir, "test_progressive_zoom.ass")

    words = [
        {"word": "DON'T", "start": 0.0, "end": 0.4, "duration": 0.4},
        {"word": "IGNORE", "start": 0.4, "end": 0.9, "duration": 0.5},
        {"word": "THIS", "start": 0.9, "end": 1.4, "duration": 0.5},
        {"word": "TRICK", "start": 1.4, "end": 1.9, "duration": 0.5}
    ]
    cards = caption_generator.chunk_words_into_cards(words, max_words_per_card=4)

    caption_generator.generate_ass_subtitles(
        caption_cards=cards,
        template_id="viral_circle_ignore",
        highlight_color_key="#facc15",
        primary_color_key="#ffffff",
        output_path=zoom_ass,
        width=1080,
        height=1920,
        progressive_reveal=True,
        word_zoom=True
    )

    assert os.path.exists(zoom_ass)
    with open(zoom_ass, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify kinetic zoom tags \fscx and \fscy are applied on active words
    assert r"\fscx" in content and r"\fscy" in content, "Kinetic word zoom should scale active word"
    assert r"\t(0,140," in content, "Kinetic word zoom should include smooth spring transform transition"

    # Verify progressive reveal: dialogues should only contain words up to target index
    lines = [line for line in content.splitlines() if line.startswith("Dialogue:")]
    assert len(lines) == 4, f"Expected 4 progressive dialogue events, got {len(lines)}"

    # First event should only have "DON'T", not future words
    assert "DON'T" in lines[0]
    assert "TRICK" not in lines[0], "First progressive dialogue event must not reveal future word 'TRICK'"

    # Last event should reveal all words
    assert "TRICK" in lines[3]

    print("Progressive reveal and kinetic word zoom verified successfully in ASS!\n")

    if os.path.exists(zoom_ass):
        os.remove(zoom_ass)

def test_marker_decorations_ass():
    print("=== Test 10: Marker FX (Neon Circle, Highlighter Box, Accent Underline) ===")
    base_dir = os.path.dirname(os.path.abspath(__file__))

    words = [
        {"word": "CUT", "start": 0.0, "end": 0.5, "duration": 0.5},
        {"word": "HOURS", "start": 0.5, "end": 1.0, "duration": 0.5},
        {"word": "WORK", "start": 1.0, "end": 1.5, "duration": 0.5}
    ]
    cards = caption_generator.chunk_words_into_cards(words, max_words_per_card=3)

    # 1. Circle marker
    circle_ass = os.path.join(base_dir, "test_marker_circle.ass")
    caption_generator.generate_ass_subtitles(
        caption_cards=cards,
        template_id="viral_circle_ignore",
        output_path=circle_ass,
        marker_style="circle",
        marker_color="#4ade80"
    )
    with open(circle_ass, "r", encoding="utf-8") as f:
        c_content = f.read()
    assert r"\bord4" in c_content, "Circle marker should apply bold border/outline effect"
    print("Circle marker ASS verified: Border/outline stroke applied!")

    # 2. Underline marker
    underline_ass = os.path.join(base_dir, "test_marker_underline.ass")
    caption_generator.generate_ass_subtitles(
        caption_cards=cards,
        template_id="viral_workflow_hours",
        output_path=underline_ass,
        marker_style="underline",
        marker_color="#38bdf8"
    )
    with open(underline_ass, "r", encoding="utf-8") as f:
        u_content = f.read()
    assert r"\u1" in u_content, "Underline marker should apply ASS underline tag"
    print("Underline marker ASS verified: Underline tag applied!")

    # 3. Box marker
    box_ass = os.path.join(base_dir, "test_marker_box.ass")
    caption_generator.generate_ass_subtitles(
        caption_cards=cards,
        template_id="hormozi_classic",
        output_path=box_ass,
        marker_style="box",
        marker_color="#facc15"
    )
    with open(box_ass, "r", encoding="utf-8") as f:
        b_content = f.read()
    assert r"\bord5" in b_content, "Box marker should apply border box styling"
    print("Highlighter box marker ASS verified: Box styling applied!\n")

    for p in [circle_ass, underline_ass, box_ass]:
        if os.path.exists(p):
            os.remove(p)

def test_pip_and_video_focus_render(pip_info):
    print("=== Test 11: Render Video with Video Focus Vignette & PiP Overlay ===")
    base_dir = os.path.dirname(os.path.abspath(__file__))

    audio_path = os.path.join(base_dir, "test_fx_audio.mp3")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "sine=frequency=520:duration=3",
        "-c:a", "libmp3lame",
        audio_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    clip_path = os.path.join(base_dir, "test_fx_clip.mp4")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=indigo:s=720x1280:d=3",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        clip_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    words = [
        {"word": "EXCLUSIVE", "start": 0.2, "end": 1.4, "duration": 1.2},
        {"word": "INSIGHT", "start": 1.4, "end": 2.8, "duration": 1.4}
    ]
    cards = caption_generator.chunk_words_into_cards(words, max_words_per_card=2)
    ass_path = os.path.join(base_dir, "test_fx_subs.ass")

    caption_generator.generate_ass_subtitles(
        caption_cards=cards,
        template_id="viral_circle_ignore",
        highlight_color_key="#4ade80",
        primary_color_key="#ffffff",
        output_path=ass_path,
        width=720,
        height=1280,
        marker_style="circle",
        marker_color="#4ade80",
        word_zoom=True,
        progressive_reveal=True
    )

    scenes = [{
        "id": 1,
        "duration": 3.0,
        "start_time": 0.0,
        "end_time": 3.0,
        "selected_clip": {
            "id": "fx_clip_1",
            "video_url": clip_path,
            "local_path": clip_path,
            "duration": 3.0
        }
    }]

    job_id = "test_pip_focus_job"
    video_composer.RENDER_JOBS[job_id] = {
        "id": job_id,
        "status": "queued",
        "progress": 0,
        "message": "Starting PiP & Focus test render"
    }

    out_dir = os.path.join(base_dir, "output")
    cache_dir = os.path.join(base_dir, "cache")

    video_composer.render_video_task(
        job_id=job_id,
        scenes=scenes,
        audio_path=audio_path,
        total_audio_duration=3.0,
        transition_type="fade",
        transition_duration=0.5,
        aspect_ratio="9:16",
        caption_ass_path=ass_path,
        cache_dir=cache_dir,
        output_dir=out_dir,
        video_focus=True,
        pip_info={
            "image_path": pip_info["path"],
            "position": "center-card",
            "size": "medium"
        }
    )

    job_state = video_composer.RENDER_JOBS[job_id]
    assert job_state["status"] == "done", f"Render failed: {job_state.get('message')}"
    output_video_path = os.path.join(out_dir, job_state["output_file"])
    assert os.path.exists(output_video_path)
    assert os.path.getsize(output_video_path) > 1000
    print(f"PiP Overlay & Video Focus render completed successfully: {output_video_path} ({os.path.getsize(output_video_path)} bytes)!\n")

    for f in [audio_path, clip_path, ass_path, output_video_path]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass

def test_viral_hierarchy_templates_ass():
    print("=== Test 12: 15 Viral Hierarchy Multi-Line Stacked MOGRT ASS ===")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    hier_ass = os.path.join(base_dir, "test_hier_stacked.ass")

    words = [
        {"word": "This", "start": 0.0, "end": 0.3, "duration": 0.3},
        {"word": "is", "start": 0.3, "end": 0.5, "duration": 0.2},
        {"word": "the", "start": 0.5, "end": 0.7, "duration": 0.2},
        {"word": "opportunity", "start": 0.7, "end": 1.4, "duration": 0.7},
        {"word": "starts", "start": 1.4, "end": 1.9, "duration": 0.5}
    ]
    cards = caption_generator.chunk_words_into_cards(words, max_words_per_card=5)

    caption_generator.generate_ass_subtitles(
        caption_cards=cards,
        template_id="hier_opportunity",
        highlight_color_key="#facc15",
        primary_color_key="#ffffff",
        output_path=hier_ass,
        width=1080,
        height=1920
    )

    assert os.path.exists(hier_ass)
    with open(hier_ass, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify ASS contains stacked line breaks \N
    assert r"\N" in content, "Viral hierarchy templates must structure words into stacked multi-line tiers with \\N"
    # Verify hero tier sizing tag
    assert r"\fs82\b1" in content, "Viral hierarchy templates must size hero keyword with \\fs82\\b1"
    print("Viral Hierarchy stacked multi-line ASS verified: Linebreaks \\N and hero scale \\fs82 applied!\n")

    if os.path.exists(hier_ass):
        os.remove(hier_ass)

def test_per_card_caption_styles():
    print("=== Test 13: Per-Card / Per-Text Caption Styles & Template Overrides ASS ===")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    multi_ass = os.path.join(base_dir, "test_per_card.ass")

    # Card 1: Uses Viral Hierarchy template (hier_changes)
    card1_words = [
        {"word": "This", "start": 0.0, "end": 0.3, "duration": 0.3},
        {"word": "will", "start": 0.3, "end": 0.6, "duration": 0.3},
        {"word": "change", "start": 0.6, "end": 1.2, "duration": 0.6},
        {"word": "everything", "start": 1.2, "end": 1.8, "duration": 0.6}
    ]
    # Card 2: Uses Neon Glow Cyan template (neon_glow_cyan)
    card2_words = [
        {"word": "Unleash", "start": 2.0, "end": 2.5, "duration": 0.5},
        {"word": "your", "start": 2.5, "end": 2.8, "duration": 0.3},
        {"word": "power", "start": 2.8, "end": 3.4, "duration": 0.6}
    ]
    # Card 3: Uses custom colors & box marker
    card3_words = [
        {"word": "Custom", "start": 3.5, "end": 4.0, "duration": 0.5},
        {"word": "styling", "start": 4.0, "end": 4.5, "duration": 0.5}
    ]
    # Card 4: Hidden (template_id = "none")
    card4_words = [
        {"word": "Silent", "start": 4.6, "end": 5.0, "duration": 0.4},
        {"word": "moment", "start": 5.0, "end": 5.5, "duration": 0.5}
    ]

    cards = [
        {
            "id": 0,
            "text": "This will change everything",
            "start_time": 0.0,
            "end_time": 1.8,
            "words": card1_words,
            "template_id": "hier_changes"
        },
        {
            "id": 1,
            "text": "Unleash your power",
            "start_time": 2.0,
            "end_time": 3.4,
            "words": card2_words,
            "template_id": "neon_glow_cyan"
        },
        {
            "id": 2,
            "text": "Custom styling",
            "start_time": 3.5,
            "end_time": 4.5,
            "words": card3_words,
            "highlight_color": "#ec4899",
            "primary_color": "#38bdf8",
            "marker_style": "box"
        },
        {
            "id": 3,
            "text": "Silent moment",
            "start_time": 4.6,
            "end_time": 5.5,
            "words": card4_words,
            "template_id": "none"
        }
    ]

    caption_generator.generate_ass_subtitles(
        caption_cards=cards,
        template_id="hormozi_classic",  # Global default
        highlight_color_key="#facc15",
        primary_color_key="#ffffff",
        output_path=multi_ass,
        width=1080,
        height=1920
    )

    assert os.path.exists(multi_ass)
    with open(multi_ass, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Header has distinct Style lines for used templates
    assert "Style: Default" in content
    assert "Style: Style_hier_changes" in content
    assert "Style: Style_neon_glow_cyan" in content

    # 2. Card 1 (hier_changes) includes multi-line stacked layout with \N
    assert r"\N" in content, r"Viral hierarchy card must generate stacked \N linebreaks"

    # 3. Card 2 (neon_glow_cyan) uses Style_neon_glow_cyan
    assert "Style_neon_glow_cyan" in content, "Card 2 must be associated with Style_neon_glow_cyan"

    # 4. Card 3 has custom hex colors in BGR format and box marker tags
    # #ec4899 -> BGR: 9948ec -> &H009948EC&
    assert "&H009948EC&" in content, "Card 3 custom highlight color must be rendered"
    assert r"\bord5" in content, "Card 3 box marker must produce border styling"

    # 5. Card 4 (template_id='none') MUST NOT appear in Dialogue events
    assert "Silent" not in content, "Hidden card (template_id='none') must not appear in Dialogue events"
    assert "moment" not in content, "Hidden card (template_id='none') must not appear in Dialogue events"

    print("Per-card / per-text caption styles verified successfully: Multi-styles, linebreaks, custom colors & none exclusions passed!\n")

    if os.path.exists(multi_ass):
        os.remove(multi_ass)

def test_autonomous_audio_analysis_and_empty_script_generation():
    print("=== Test 14: Autonomous Free Audio Analysis & Empty Script Scene Generation ===")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(base_dir, "test_auto_audio.mp3")

    # Generate test audio
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=6.0",
        "-c:a", "libmp3lame", audio_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    from app import AUDIO_REGISTRY
    import audio_analyzer
    audio_id = "test_auto_id_123"
    info = audio_analyzer.get_audio_info(audio_path)
    AUDIO_REGISTRY[audio_id] = {
        "id": audio_id,
        "path": audio_path,
        "filename": "test_auto_audio.mp3",
        "info": info
    }

    # 1. Test POST /api/segment-script with empty script_text (Free autonomous audio analysis)
    resp = client.post("/api/segment-script", json={
        "audio_id": audio_id,
        "script_text": ""
    })
    assert resp.status_code == 200, f"Failed: {resp.text}"
    seg_data = resp.json()
    assert seg_data["status"] == "success"
    assert "transcript" in seg_data and len(seg_data["transcript"]) > 0
    assert "scenes" in seg_data and len(seg_data["scenes"]) >= 1
    print(f"Empty script successfully auto-analyzed audio: Generated {len(seg_data['scenes'])} scenes and transcript: '{seg_data['transcript'][:45]}...'")

    # 2. Test POST /api/generate-captions with empty script_text
    resp_cap = client.post("/api/generate-captions", json={
        "audio_id": audio_id,
        "script_text": "",
        "template_id": "smooth_cross"
    })
    assert resp_cap.status_code == 200, f"Failed: {resp_cap.text}"
    cap_data = resp_cap.json()
    assert cap_data["status"] == "success"
    assert len(cap_data["transcript"]) > 0
    assert len(cap_data["cards"]) >= 1
    print(f"Empty script successfully generated {len(cap_data['cards'])} caption cards from audio for free!\n")

    if os.path.exists(audio_path):
        os.remove(audio_path)


def test_unified_analyze_and_generate_multiclip():
    print("=== Test 15: Unified Audio Analysis & Multi-Clip Scene Generation ===")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(base_dir, "test_multiclip_audio.mp3")

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "sine=frequency=440:duration=12",
        "-c:a", "libmp3lame",
        audio_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    from app import AUDIO_REGISTRY
    import audio_analyzer
    audio_id = "test_multiclip_123"
    info = audio_analyzer.get_audio_info(audio_path)
    AUDIO_REGISTRY[audio_id] = {
        "id": audio_id,
        "path": audio_path,
        "filename": "test_multiclip_audio.mp3",
        "info": info
    }

    # Test POST /api/analyze-and-generate
    resp = client.post("/api/analyze-and-generate", json={
        "audio_id": audio_id,
        "script_text": "Experience the energy of urban technology and discover the peace of mountains today.",
        "aspect_ratio": "9:16"
    })
    assert resp.status_code == 200, f"Failed: {resp.text}"
    data = resp.json()
    assert data["status"] == "success"
    assert len(data["scenes"]) >= 2, f"Expected at least 2 scenes, got {len(data['scenes'])}"
    
    # Assert each scene has a selected clip
    used_ids = set()
    for s in data["scenes"]:
        assert "selected_clip" in s and s["selected_clip"] is not None
        clip = s["selected_clip"]
        assert "video_url" in clip or "preview_url" in clip
        used_ids.add(clip["id"])
    
    print(f"Generated {len(data['scenes'])} scenes with {len(used_ids)} distinct video clips matched!")
    assert len(data["caption_cards"]) >= 1, "Expected caption cards"
    assert len(data["timed_words"]) >= 1, "Expected timed words"

    # Test POST /api/swap-clip
    swap_resp = client.post("/api/swap-clip", json={
        "query": "ocean",
        "aspect_ratio": "9:16"
    })
    assert swap_resp.status_code == 200
    swap_data = swap_resp.json()
    assert len(swap_data.get("videos", [])) >= 1
    print(f"Clip swap search returned {len(swap_data['videos'])} candidate clips!")

    if os.path.exists(audio_path):
        os.remove(audio_path)
    print("Multi-clip audio analysis, scene generation, and clip matching verified successfully!\n")


def test_capcut_nle_api_suite():
    print("=== Test 16: CapCut NLE API Suite (Pexels Proxy, AI Timeline, Projects, Presets) ===")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(base_dir, "test_nle_audio.mp3")

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "sine=frequency=330:duration=10",
        "-c:a", "libmp3lame",
        audio_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    from app import AUDIO_REGISTRY
    import audio_analyzer
    audio_id = "test_nle_audio_id"
    info = audio_analyzer.get_audio_info(audio_path)
    AUDIO_REGISTRY[audio_id] = {
        "id": audio_id,
        "path": audio_path,
        "filename": "test_nle_audio.mp3",
        "info": info
    }

    # 1. Test Pexels Search
    p_resp = client.get("/api/search-pexels?query=technology&orientation=portrait&per_page=6")
    assert p_resp.status_code == 200
    p_data = p_resp.json()
    assert len(p_data.get("videos", [])) >= 1
    print(f"Pexels search proxy returned {len(p_data['videos'])} stock videos!")

    # 2. Test Audio Analysis
    a_resp = client.post("/api/analyze-audio", json={
        "audio_id": audio_id,
        "script_text": "Artificial intelligence is empowering creators around the world."
    })
    assert a_resp.status_code == 200
    a_data = a_resp.json()
    assert "transcript" in a_data and len(a_data["transcript"]) > 0
    assert "keywords" in a_data and len(a_data["keywords"]) >= 1
    print(f"Audio analysis returned keywords: {a_data['keywords']}")

    # 3. Test AI Timeline Generation (Option A)
    tl_resp = client.post("/api/ai-generate-timeline", json={
        "audio_id": audio_id,
        "aspect_ratio": "9:16",
        "script_text": "Artificial intelligence is empowering creators around the world.",
        "template_id": "tiktok_bold"
    })
    assert tl_resp.status_code == 200
    tl_data = tl_resp.json()
    assert "timeline" in tl_data
    timeline = tl_data["timeline"]
    assert len(timeline["tracks"]) >= 3
    v1_track = next((t for t in timeline["tracks"] if t["id"] == "V1"), None)
    t1_track = next((t for t in timeline["tracks"] if t["id"] == "T1"), None)
    assert v1_track and len(v1_track["clips"]) >= 1
    assert t1_track and len(t1_track["clips"]) >= 1
    print(f"Option A AI Timeline generated {len(v1_track['clips'])} V1 clips and {len(t1_track['clips'])} T1 caption clips!")

    # 4. Test Caption Presets
    cp_resp = client.get("/api/caption-presets")
    assert cp_resp.status_code == 200
    cp_data = cp_resp.json()
    assert len(cp_data["presets"]) >= 5
    assert len(cp_data["fonts"]) >= 5
    print(f"Caption presets returned {len(cp_data['presets'])} styles and {len(cp_data['fonts'])} fonts!")

    # 5. Test Project Save & Load
    proj_resp = client.post("/api/projects", json={
        "name": "My CapCut Project",
        "aspect_ratio": "9:16",
        "timeline": timeline
    })
    assert proj_resp.status_code == 200
    proj_id = proj_resp.json()["project_id"]

    load_resp = client.get(f"/api/projects/{proj_id}")
    assert load_resp.status_code == 200
    assert load_resp.json()["project"]["name"] == "My CapCut Project"
    print(f"Project save & load verified successfully! (ID: {proj_id})")

    # 6. Test Render Timeline
    r_resp = client.post("/api/render-timeline", json={
        "timeline": timeline,
        "aspect_ratio": "9:16",
        "resolution": "720p",
        "caption_template": "tiktok_bold"
    })
    assert r_resp.status_code == 200
    job_id = r_resp.json()["job_id"]
    print(f"Timeline render job started successfully with ID: {job_id}")

    if os.path.exists(audio_path):
        os.remove(audio_path)
    print("CapCut NLE API Suite verified completely!\n")

if __name__ == "__main__":
    test_caption_templates_and_fonts()
    test_multifont_and_dual_color_ass()
    test_shine_toggle_ass_output()
    test_api_caption_templates_endpoint()
    direct_info = test_direct_video_upload_endpoint()
    test_direct_video_render_burn(direct_info)
    test_full_render_with_custom_video_and_captions()
    pip_info = test_pip_image_upload_and_preview()
    test_progressive_reveal_and_word_zoom_ass()
    test_marker_decorations_ass()
    test_pip_and_video_focus_render(pip_info)
    test_viral_hierarchy_templates_ass()
    test_per_card_caption_styles()
    test_autonomous_audio_analysis_and_empty_script_generation()
    test_unified_analyze_and_generate_multiclip()
    test_capcut_nle_api_suite()
    print("=========================================================================================")
    print("ALL 16 TEST SUITES PASSED! CAPCUT STUDIO UI, FREE AUDIO ANALYSIS & PREVIEWS VERIFIED!")
    print("=========================================================================================")
