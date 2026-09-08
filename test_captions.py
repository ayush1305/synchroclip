import os
import sys
import json
import subprocess

server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server")
sys.path.insert(0, server_dir)

import caption_templates
import caption_generator
import video_composer

def test_caption_pipeline():
    print("=== Step 1: Testing Caption Templates ===")
    templates = caption_templates.TEMPLATES
    assert "capcut_classic" in templates
    assert "neon_fox" in templates
    assert "red_fire" in templates
    assert "word_pop" in templates
    assert "cinematic_serif" in templates
    print(f"Loaded {len(templates)} templates successfully!")

    print("=== Step 2: Testing Speech/Word Alignment ===")
    test_audio = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_audio_cap.mp3")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "sine=frequency=330:duration=8",
        "-c:a", "libmp3lame",
        test_audio
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    script = "Create stunning videos with automatic captions and word highlights."
    words = caption_generator.align_words_to_timeline(script, test_audio, 8.0)
    print(f"Aligned {len(words)} words:")
    for w in words[:4]:
        print(f"  Word: '{w['word']}' [{w['start']}s -> {w['end']}s]")
    assert len(words) >= 8, "Expected at least 8 aligned words"

    cards = caption_generator.chunk_words_into_cards(words, max_words_per_card=3)
    print(f"Grouped into {len(cards)} caption cards.")
    assert len(cards) >= 2

    print("=== Step 3: Testing ASS Subtitle File Generation ===")
    ass_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_subtitles.ass")
    caption_generator.generate_ass_subtitles(
        caption_cards=cards,
        template_id="capcut_classic",
        highlight_color_key="yellow",
        output_path=ass_path,
        width=1920,
        height=1080
    )
    assert os.path.exists(ass_path), "ASS file was not generated"
    with open(ass_path, "r", encoding="utf-8") as f:
        ass_content = f.read()
    assert "Dialogue:" in ass_content
    assert "\\c&H0000FFFF&" in ass_content  # Yellow highlight tag
    print("ASS file generated with word highlight tags!\n")

    print("=== Step 4: Testing FFmpeg ASS Burning onto Video ===")
    clip = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_bg_clip.mp4")
    out_video = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_captioned_video.mp4")
    
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=navy:s=640x360:d=8",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        clip
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    scenes = [{
        "id": 1,
        "duration": 8.0,
        "selected_clip": {"id": "c1", "video_url": clip}
    }]

    job_id = "test_cap_job"
    video_composer.RENDER_JOBS[job_id] = {"status": "queued", "progress": 0, "message": "Testing captions"}

    video_composer.render_video_task(
        job_id=job_id,
        scenes=scenes,
        audio_path=test_audio,
        total_audio_duration=8.0,
        aspect_ratio="16:9",
        caption_ass_path=ass_path,
        cache_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache"),
        output_dir=os.path.dirname(out_video)
    )

    assert video_composer.RENDER_JOBS[job_id]["status"] == "done", "Render with captions failed"
    print("Rendered video with burned CapCut captions successfully!")

    # Cleanup test files
    for f in [test_audio, clip, ass_path, out_video]:
        if os.path.exists(f):
            os.remove(f)

    print("\nALL CAPTION PIPELINE TESTS PASSED! SUCCESS!")

if __name__ == "__main__":
    test_caption_pipeline()
