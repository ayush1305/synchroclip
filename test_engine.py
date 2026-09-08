import os
import sys
import subprocess
import json

# Add server directory to path
server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server")
sys.path.insert(0, server_dir)

import audio_analyzer
import text_segmenter
import pexels_client
import video_composer

def test_pipeline():
    print("=== Step 1: Testing Audio Generator & Analyzer ===")
    test_audio = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_audio.mp3")
    
    # Generate 10-second sine wave audio
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "sine=frequency=440:duration=10",
        "-c:a", "libmp3lame",
        test_audio
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    assert os.path.exists(test_audio), "Test audio creation failed"

    info = audio_analyzer.get_audio_info(test_audio)
    print(f"Audio duration: {info['duration']}s, sample_rate: {info['sample_rate']}")
    assert abs(info['duration'] - 10.0) < 0.2, f"Expected ~10.0s, got {info['duration']}"

    peaks = audio_analyzer.get_waveform_peaks(test_audio, 20)
    print(f"Waveform peaks count: {len(peaks)}, sample values: {peaks[:4]}")
    assert len(peaks) == 20, "Waveform length mismatch"
    print("Audio Analyzer test passed!\n")

    print("=== Step 2: Testing Text Segmenter & Time Allocation ===")
    script = "The morning light breaks through the forest trees. Every moment is a chance to begin anew."
    scenes = text_segmenter.segment_script_and_allocate_time(script, info['duration'])
    print(f"Scenes count: {len(scenes)}")
    for s in scenes:
        print(f"  Scene #{s['id']}: [{s['formatted_time']}] dur={s['duration']}s | query: '{s['primary_query']}' | text: '{s['text']}'")

    total_scene_dur = sum(s['duration'] for s in scenes)
    print(f"Total scene durations: {total_scene_dur:.2f}s vs Audio: {info['duration']:.2f}s")
    assert abs(total_scene_dur - info['duration']) < 0.1, "Duration sum mismatch"
    print("Text Segmenter test passed!\n")

    print("=== Step 3: Testing Pexels Client & Fallbacks ===")
    res = pexels_client.search_pexels_videos("morning forest", api_key="", orientation="landscape")
    print(f"Pexels search source: {res['source']}, found: {len(res['videos'])} videos")
    assert len(res['videos']) > 0, "No videos returned"
    print("Pexels Client test passed!\n")

    print("=== Step 4: Testing FFmpeg XFade Composition Engine ===")
    # Create two 4-second colored test video clips
    clip1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_clip1.mp4")
    clip2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_clip2.mp4")

    # Cyan clip
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=navy:s=640x360:d=5",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        clip1
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Orange clip
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=darkorange:s=640x360:d=5",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        clip2
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Assign clips to 2 scenes
    scenes[0]["selected_clip"] = {"id": "test1", "video_url": clip1}
    scenes[1]["selected_clip"] = {"id": "test2", "video_url": clip2}

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")

    job_id = "test_job_123"
    video_composer.RENDER_JOBS[job_id] = {"status": "queued", "progress": 0, "message": "Test"}
    
    print("Running render_video_task...")
    video_composer.render_video_task(
        job_id=job_id,
        scenes=scenes,
        audio_path=test_audio,
        total_audio_duration=info['duration'],
        transition_type="dissolve",
        transition_duration=0.6,
        aspect_ratio="16:9",
        cache_dir=cache_dir,
        output_dir=output_dir
    )

    job_res = video_composer.RENDER_JOBS[job_id]
    print(f"Render job result: {job_res['status']}, output: {job_res.get('output_file')}")
    assert job_res['status'] == "done", f"Render failed: {job_res.get('message')}"

    out_file = os.path.join(output_dir, job_res['output_file'])
    assert os.path.exists(out_file), "Output MP4 not found"

    # Verify generated video with ffprobe
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-show_entries", "stream=codec_type,codec_name",
        "-of", "json",
        out_file
    ]
    probe_out = subprocess.run(probe_cmd, stdout=subprocess.PIPE, text=True, check=True)
    meta = json.loads(probe_out.stdout)
    out_dur = float(meta['format']['duration'])
    streams = [s['codec_type'] for s in meta['streams']]
    print(f"Rendered video streams: {streams}, duration: {out_dur:.2f}s")
    assert "video" in streams, "Missing video stream"
    assert "audio" in streams, "Missing audio stream"
    assert abs(out_dur - info['duration']) < 0.5, f"Output duration {out_dur} does not match audio {info['duration']}"

    # Clean up test artifacts
    for f in [test_audio, clip1, clip2]:
        if os.path.exists(f):
            os.remove(f)

    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY! SUCCESS!")

if __name__ == "__main__":
    test_pipeline()
