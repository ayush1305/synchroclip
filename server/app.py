import os
import uuid
import shutil
import json
import subprocess
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import audio_analyzer
import text_segmenter
import pexels_client
import video_composer
import caption_templates
import caption_generator
import zipfile

import sys

# Resolve base directories (supporting standalone PyInstaller frozen app)
if getattr(sys, 'frozen', False):
    APP_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    APP_DIR = BASE_DIR

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
VIDEO_UPLOAD_DIR = os.path.join(UPLOAD_DIR, "videos")
DIRECT_VIDEO_DIR = os.path.join(UPLOAD_DIR, "direct_videos")
PIP_UPLOAD_DIR = os.path.join(UPLOAD_DIR, "pip")
AUDIO_DIR = os.path.join(UPLOAD_DIR, "audio")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CACHE_DIR = os.path.join(BASE_DIR, "cache")
STATIC_DIR = os.path.join(APP_DIR, "static")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VIDEO_UPLOAD_DIR, exist_ok=True)
os.makedirs(DIRECT_VIDEO_DIR, exist_ok=True)
os.makedirs(PIP_UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

app = FastAPI(title="AI Audio-Synced Stock Video Studio", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_header(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# In-memory store for uploaded audio files
AUDIO_REGISTRY = {}

class SegmentRequest(BaseModel):
    audio_id: str
    script_text: str
    min_segment_duration: Optional[float] = 3.2
    max_segment_duration: Optional[float] = 8.0

class PexelsSearchRequest(BaseModel):
    query: str
    api_key: Optional[str] = None
    orientation: Optional[str] = "landscape"
    per_page: Optional[int] = 12

class AutoMatchRequest(BaseModel):
    scenes: list[dict]
    api_key: Optional[str] = None
    orientation: Optional[str] = "landscape"

class CaptionRequest(BaseModel):
    audio_id: str
    script_text: Optional[str] = ""
    template_id: Optional[str] = "capcut_classic"
    is_word_pop: Optional[bool] = False

class RenderRequest(BaseModel):
    audio_id: str
    scenes: Optional[list[dict]] = None
    transition_type: Optional[str] = "fade"
    transition_duration: Optional[float] = 0.8
    aspect_ratio: Optional[str] = "16:9"
    caption_template: Optional[str] = "none"
    primary_color: Optional[str] = None
    highlight_color: Optional[str] = "yellow"
    caption_cards: Optional[list[dict]] = None
    font_family: Optional[str] = None
    hero_font: Optional[str] = None
    is_direct_video: Optional[bool] = False
    direct_video_path: Optional[str] = None
    enable_shine: Optional[bool] = False
    progressive_reveal: Optional[bool] = False
    word_zoom: Optional[bool] = False
    marker_style: Optional[str] = "none"
    marker_color: Optional[str] = "#4ade80"
    video_focus: Optional[bool] = False
    pip_image_path: Optional[str] = None
    pip_position: Optional[str] = "top-right"
    pip_size: Optional[str] = "medium"

def get_video_info_and_thumb(video_path: str, thumb_path: str) -> dict:
    duration = 0.0
    width = 1920
    height = 1080
    try:
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            video_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        data = json.loads(res.stdout)
        duration = float(data.get("format", {}).get("duration", 0))
        for s in data.get("streams", []):
            if s.get("codec_type") == "video":
                width = int(s.get("width", 1920))
                height = int(s.get("height", 1080))
                if duration == 0 and "duration" in s:
                    try:
                        duration = float(s["duration"])
                    except Exception:
                        pass
                break
    except Exception as e:
        print(f"Warning: ffprobe failed on {video_path}: {e}")

    try:
        seek_pos = "00:00:01.000" if duration > 1.5 else "00:00:00.100"
        thumb_cmd = [
            "ffmpeg", "-y",
            "-ss", seek_pos,
            "-i", video_path,
            "-vframes", "1",
            "-vf", "scale=640:-2",
            "-q:v", "3",
            thumb_path
        ]
        subprocess.run(thumb_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception as e:
        try:
            fallback_cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-vframes", "1",
                "-q:v", "3",
                thumb_path
            ]
            subprocess.run(fallback_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    return {
        "duration": round(duration, 2),
        "width": width,
        "height": height
    }

@app.post("/api/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    Uploads an audio file, extracts duration, metadata, and waveform peaks.
    """
    try:
        audio_id = uuid.uuid4().hex[:10]
        ext = os.path.splitext(file.filename)[1] or ".mp3"
        safe_filename = f"{audio_id}{ext}"
        target_path = os.path.join(UPLOAD_DIR, safe_filename)

        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Analyze audio via ffprobe
        info = audio_analyzer.get_audio_info(target_path)
        waveform = audio_analyzer.get_waveform_peaks(target_path, num_points=70)

        AUDIO_REGISTRY[audio_id] = {
            "id": audio_id,
            "filename": file.filename,
            "path": target_path,
            "info": info
        }

        return {
            "status": "success",
            "audio_id": audio_id,
            "filename": file.filename,
            "duration": info["duration"],
            "formatted_duration": info["formatted_duration"],
            "sample_rate": info["sample_rate"],
            "channels": info["channels"],
            "waveform": waveform
        }
    except Exception as e:
        print(f"Error processing audio upload: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to process audio: {str(e)}")

@app.get("/api/audio/{audio_id}")
async def get_audio_stream(audio_id: str):
    """
    Streams the uploaded audio file to the browser player.
    """
    if audio_id not in AUDIO_REGISTRY:
        # Check if file exists directly on disk
        for f in os.listdir(UPLOAD_DIR):
            if f.startswith(audio_id):
                return FileResponse(os.path.join(UPLOAD_DIR, f))
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(AUDIO_REGISTRY[audio_id]["path"])

@app.post("/api/segment-script")
async def segment_script(req: SegmentRequest):
    """
    Breaks transcript into scene segments matching total audio duration.
    If script_text is empty, automatically analyzes and transcribes audio for free!
    """
    if req.audio_id not in AUDIO_REGISTRY:
        raise HTTPException(status_code=404, detail="Audio ID not found. Please upload audio first.")

    audio_entry = AUDIO_REGISTRY[req.audio_id]
    audio_path = audio_entry["path"]
    total_duration = audio_entry["info"]["duration"]

    text = req.script_text.strip() if req.script_text else ""
    if not text:
        # Auto-transcribe audio file for free
        text = caption_generator.transcribe_audio_file(audio_path)

    scenes = text_segmenter.segment_script_and_allocate_time(
        script_text=text,
        total_duration=total_duration,
        min_segment_duration=req.min_segment_duration or 3.2,
        max_segment_duration=req.max_segment_duration or 8.0
    )

    return {
        "status": "success",
        "transcript": text,
        "total_duration": total_duration,
        "scenes": scenes
    }

@app.post("/api/search-pexels")
async def search_pexels(req: PexelsSearchRequest):
    """
    Searches Pexels Video API for clips matching query.
    """
    results = pexels_client.search_pexels_videos(
        query=req.query,
        api_key=req.api_key,
        orientation=req.orientation or "landscape",
        per_page=req.per_page or 12
    )
    return results

@app.post("/api/auto-match-all")
async def auto_match_all(req: AutoMatchRequest):
    """
    For all scenes, automatically selects the best matching clip from Pexels.
    """
    updated_scenes = []
    used_clip_ids = set()

    for scene in req.scenes:
        query = scene.get("primary_query") or "cinematic view"
        res = pexels_client.search_pexels_videos(
            query=query,
            api_key=req.api_key,
            orientation=req.orientation or "landscape",
            per_page=8
        )
        videos = res.get("videos", [])
        
        # Pick the best clip not already used if possible
        chosen_clip = None
        for v in videos:
            if v["id"] not in used_clip_ids:
                chosen_clip = v
                used_clip_ids.add(v["id"])
                break
        
        if not chosen_clip and videos:
            chosen_clip = videos[0]

        scene_copy = dict(scene)
        scene_copy["selected_clip"] = chosen_clip
        updated_scenes.append(scene_copy)

    return {
        "status": "success",
        "scenes": updated_scenes
    }

@app.post("/api/render")
async def render_video(req: RenderRequest):
    """
    Initiates background rendering of the final video using FFmpeg.
    """
    if req.audio_id not in AUDIO_REGISTRY:
        raise HTTPException(status_code=404, detail="Audio ID not found")

    audio_entry = AUDIO_REGISTRY[req.audio_id]
    audio_path = audio_entry["path"]
    total_audio_duration = audio_entry["info"]["duration"]

    # Generate ASS subtitles if a caption template or custom card template is selected
    caption_ass_path = None
    has_active_captions = (req.caption_template and req.caption_template != "none") or any(
        c.get("template_id") and c.get("template_id") != "none" for c in (req.caption_cards or [])
    )
    if has_active_captions and req.caption_cards:
        sub_filename = f"captions_{uuid.uuid4().hex[:8]}.ass"
        sub_path = os.path.join(OUTPUT_DIR, sub_filename)
        width = 1080 if req.aspect_ratio == "9:16" else 1920
        height = 1920 if req.aspect_ratio == "9:16" else 1080
        caption_generator.generate_ass_subtitles(
            caption_cards=req.caption_cards,
            template_id=req.caption_template or "hormozi_classic",
            highlight_color_key=req.highlight_color or "yellow",
            primary_color_key=req.primary_color,
            output_path=sub_path,
            width=width,
            height=height,
            font_family_override=req.font_family,
            hero_font_override=req.hero_font,
            enable_shine=bool(req.enable_shine),
            progressive_reveal=bool(req.progressive_reveal),
            word_zoom=bool(req.word_zoom),
            marker_style=req.marker_style or "none",
            marker_color=req.marker_color or "#4ade80"
        )
        caption_ass_path = sub_path

    pip_info = None
    if req.pip_image_path and os.path.exists(req.pip_image_path):
        pip_info = {
            "image_path": req.pip_image_path,
            "position": req.pip_position or "top-right",
            "size": req.pip_size or "medium"
        }

    # Direct Video Mode (Bypass stock scenes and burn subtitles directly onto pre-existing video)
    if req.is_direct_video and req.direct_video_path and os.path.exists(req.direct_video_path):
        job_id = video_composer.start_direct_render_job(
            video_path=req.direct_video_path,
            caption_ass_path=caption_ass_path,
            output_dir=OUTPUT_DIR,
            video_focus=bool(req.video_focus),
            pip_info=pip_info
        )
        return {
            "status": "started",
            "job_id": job_id
        }

    if not req.scenes:
        raise HTTPException(status_code=400, detail="No scenes provided for rendering")

    job_id = video_composer.start_render_job(
        scenes=req.scenes,
        audio_path=audio_path,
        total_audio_duration=total_audio_duration,
        transition_type=req.transition_type or "fade",
        transition_duration=req.transition_duration or 0.8,
        aspect_ratio=req.aspect_ratio or "16:9",
        caption_ass_path=caption_ass_path,
        cache_dir=CACHE_DIR,
        output_dir=OUTPUT_DIR,
        video_focus=bool(req.video_focus),
        pip_info=pip_info
    )

    return {
        "status": "started",
        "job_id": job_id
    }

@app.post("/api/upload-direct-video")
async def upload_direct_video(file: UploadFile = File(...)):
    """
    Uploads an entire pre-existing video (.mp4, .mov, .webm, .mkv).
    Extracts audio track, analyzes duration/waveform, and registers audio
    so the user can immediately transcribe and add animated captions directly without generating stock clips!
    """
    try:
        ext = os.path.splitext(file.filename)[1].lower() or ".mp4"
        valid_exts = {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"}
        if ext not in valid_exts:
            raise HTTPException(status_code=400, detail=f"Unsupported format '{ext}'. Allowed: MP4, MOV, WebM, MKV.")

        video_id = uuid.uuid4().hex[:10]
        audio_id = f"audio_{video_id}"
        safe_video_name = f"direct_{video_id}{ext}"
        safe_thumb_name = f"direct_{video_id}_thumb.jpg"
        safe_audio_name = f"audio_{video_id}.mp3"

        target_video_path = os.path.join(DIRECT_VIDEO_DIR, safe_video_name)
        target_thumb_path = os.path.join(DIRECT_VIDEO_DIR, safe_thumb_name)
        target_audio_path = os.path.join(AUDIO_DIR, safe_audio_name)

        with open(target_video_path, "wb") as buf:
            shutil.copyfileobj(file.file, buf)

        info = get_video_info_and_thumb(target_video_path, target_thumb_path)

        # Extract audio track to MP3
        cmd_audio = [
            "ffmpeg", "-y",
            "-i", target_video_path,
            "-vn",
            "-acodec", "libmp3lame",
            "-ar", "44100",
            "-ab", "192k",
            target_audio_path
        ]
        subprocess.run(cmd_audio, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        audio_info = audio_analyzer.get_audio_info(target_audio_path)
        waveform = audio_analyzer.get_waveform_peaks(target_audio_path, num_points=70)

        AUDIO_REGISTRY[audio_id] = {
            "id": audio_id,
            "filename": f"Extracted from {file.filename}",
            "path": target_audio_path,
            "info": audio_info
        }

        return {
            "status": "success",
            "video_id": video_id,
            "audio_id": audio_id,
            "filename": file.filename,
            "video_url": f"/uploads/direct_videos/{safe_video_name}",
            "local_video_path": target_video_path,
            "thumb_url": f"/uploads/direct_videos/{safe_thumb_name}" if os.path.exists(target_thumb_path) else "",
            "duration": audio_info["duration"],
            "formatted_duration": audio_info["formatted_duration"],
            "width": info["width"],
            "height": info["height"],
            "waveform": waveform
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error handling direct video upload: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process video: {str(e)}")

@app.post("/api/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """
    Uploads a user video clip (.mp4, .mov, .webm, .mkv), extracts duration & dimensions,
    generates a thumbnail, and returns clip metadata ready for storyboard integration.
    """
    try:
        ext = os.path.splitext(file.filename)[1].lower() or ".mp4"
        valid_exts = {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"}
        if ext not in valid_exts:
            raise HTTPException(status_code=400, detail=f"Unsupported video format '{ext}'. Allowed: MP4, MOV, WebM, MKV.")

        video_id = uuid.uuid4().hex[:10]
        safe_name = f"user_{video_id}{ext}"
        thumb_name = f"user_{video_id}_thumb.jpg"
        target_video_path = os.path.join(VIDEO_UPLOAD_DIR, safe_name)
        target_thumb_path = os.path.join(VIDEO_UPLOAD_DIR, thumb_name)

        with open(target_video_path, "wb") as buf:
            shutil.copyfileobj(file.file, buf)

        info = get_video_info_and_thumb(target_video_path, target_thumb_path)
        base_title = os.path.splitext(file.filename)[0]

        return {
            "status": "success",
            "clip": {
                "id": f"upload_{video_id}",
                "title": f"My Video: {base_title[:24]}",
                "video_url": f"/uploads/videos/{safe_name}",
                "local_path": target_video_path,
                "preview_url": f"/uploads/videos/{thumb_name}" if os.path.exists(target_thumb_path) else f"/uploads/videos/{safe_name}",
                "image": f"/uploads/videos/{thumb_name}" if os.path.exists(target_thumb_path) else "",
                "duration": info["duration"],
                "width": info["width"],
                "height": info["height"],
                "author": "My Upload",
                "is_user_upload": True
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error handling video upload: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process video: {str(e)}")

@app.post("/api/upload-pip-image")
async def upload_pip_image(file: UploadFile = File(...)):
    """
    Uploads a picture-in-picture (PiP) overlay image (.png, .jpg, .jpeg, .webp, .svg).
    """
    try:
        ext = os.path.splitext(file.filename)[1].lower() or ".png"
        valid_exts = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
        if ext not in valid_exts:
            raise HTTPException(status_code=400, detail=f"Unsupported image format '{ext}'. Allowed: PNG, JPG, JPEG, WEBP, SVG.")

        img_id = uuid.uuid4().hex[:10]
        safe_name = f"pip_{img_id}{ext}"
        target_path = os.path.join(PIP_UPLOAD_DIR, safe_name)

        with open(target_path, "wb") as buf:
            shutil.copyfileobj(file.file, buf)

        return {
            "status": "success",
            "pip_id": img_id,
            "filename": file.filename,
            "url": f"/uploads/pip/{safe_name}",
            "pip_url": f"/uploads/pip/{safe_name}",
            "path": target_path,
            "local_path": target_path
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error handling PiP image upload: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process PiP image: {str(e)}")

@app.get("/api/render-status/{job_id}")
async def get_render_status(job_id: str):
    """
    Checks progress status of a video rendering job.
    """
    if job_id not in video_composer.RENDER_JOBS:
        raise HTTPException(status_code=404, detail="Job not found")

    job = video_composer.RENDER_JOBS[job_id]
    resp = {
        "id": job["id"],
        "status": job["status"],
        "progress": job["progress"],
        "message": job["message"]
    }

    if job["status"] == "done" and job.get("output_file"):
        resp["download_url"] = f"/api/download/{job['output_file']}"
        resp["video_url"] = f"/api/download/{job['output_file']}"
        resp["output_file"] = job["output_file"]

    return resp

@app.get("/api/download/{filename}")
async def download_output(filename: str):
    """
    Serves the final rendered MP4 video.
    """
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="video/mp4", filename=filename)

@app.get("/api/sample-demo")
async def get_sample_demo():
    """
    Generates or provides a built-in demo audio + script so the user can test immediately with 1 click.
    """
    demo_filename = "demo_ambient_voice.mp3"
    demo_path = os.path.join(UPLOAD_DIR, demo_filename)
    
    # If demo audio doesn't exist, create an ambient synthesizer audio track using ffmpeg
    if not os.path.exists(demo_path):
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "sine=frequency=220:duration=18",
            "-filter_complex", "volume=0.3,aecho=0.8:0.88:60:0.4",
            "-c:a", "libmp3lame",
            demo_path
        ]
        try:
            import subprocess
            subprocess.run(cmd, check=True)
        except Exception as e:
            print(f"Error creating sample audio: {e}")

    demo_id = "sample-demo-1"
    info = audio_analyzer.get_audio_info(demo_path)
    waveform = audio_analyzer.get_waveform_peaks(demo_path, num_points=70)
    
    AUDIO_REGISTRY[demo_id] = {
        "id": demo_id,
        "filename": "demo_ambient_track.mp3",
        "path": demo_path,
        "info": info
    }

    sample_script = (
        "Every morning brings a fresh start and a world full of opportunities. "
        "When you focus your mind and step into nature, ideas begin to flow naturally. "
        "Keep moving forward with purpose, and create something extraordinary today."
    )

    return {
        "status": "success",
        "audio_id": demo_id,
        "filename": "demo_ambient_track.mp3",
        "duration": info["duration"],
        "formatted_duration": info["formatted_duration"],
        "waveform": waveform,
        "script": sample_script
    }

@app.get("/api/caption-templates")
async def get_caption_templates():
    """
    Returns available CapCut-style caption templates, highlight color palette, and famous fonts.
    """
    return {
        "status": "success",
        "templates": list(caption_templates.TEMPLATES.values()),
        "colors": caption_templates.HIGHLIGHT_COLORS,
        "famous_fonts": caption_templates.FAMOUS_FONTS,
        "marker_styles": caption_templates.MARKER_STYLES
    }

@app.post("/api/generate-captions")
async def generate_captions(req: CaptionRequest):
    """
    Transcribes audio or aligns provided script into word-level timestamps and caption cards.
    """
    if req.audio_id not in AUDIO_REGISTRY:
        raise HTTPException(status_code=404, detail="Audio ID not found")

    audio_entry = AUDIO_REGISTRY[req.audio_id]
    audio_path = audio_entry["path"]
    total_duration = audio_entry["info"]["duration"]

    text = req.script_text.strip() if req.script_text else ""
    if not text:
        # Automated Speech-to-Text transcription
        text = caption_generator.transcribe_audio_file(audio_path)
        if not text:
            text = "Welcome to this inspiring moment. Create something incredible today."

    timed_words = caption_generator.align_words_to_timeline(text, audio_path, total_duration)
    is_pop = (req.template_id == "word_pop")
    cards = caption_generator.chunk_words_into_cards(timed_words, is_word_pop=is_pop, max_words_per_card=4)

    return {
        "status": "success",
        "transcript": text,
        "words": timed_words,
        "cards": cards
    }

@app.get("/api/download-project-zip")
async def download_project_zip():
    """
    Generates a clean downloadable ZIP archive of the entire application codebase.
    """
    zip_path = os.path.join(OUTPUT_DIR, "synchroclip-studio.zip")
    
    exclude_dirs = {"uploads", "cache", "output", ".git", "__pycache__", ".pytest_cache"}
    exclude_exts = {".pyc", ".tmp", ".log", ".mp4", ".mp3", ".wav"}

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(BASE_DIR):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if any(file.endswith(ext) for ext in exclude_exts):
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, BASE_DIR)
                zipf.write(file_path, arcname=rel_path)

    return FileResponse(zip_path, media_type="application/zip", filename="synchroclip-studio.zip")

@app.get("/api/download-app-exe")
async def download_app_exe():
    """
    Direct standalone Windows Executable (.exe) download - no zip needed.
    """
    exe_path = os.path.join(BASE_DIR, "dist", "SynchroClip.exe")
    if not os.path.exists(exe_path):
        raise HTTPException(status_code=404, detail="Standalone executable not found.")
    return FileResponse(exe_path, media_type="application/vnd.microsoft.portable-executable", filename="SynchroClip.exe")

@app.get("/api/git-info")
async def get_git_info():
    """
    Returns step-by-step instructions for publishing this repo to GitHub.
    """
    return {
        "status": "success",
        "steps": [
            "git init",
            "git add .",
            "git commit -m 'Initial commit of SynchroClip Studio'",
            "git branch -M main",
            "git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO_NAME>.git",
            "git push -u origin main"
        ]
    }

# Mount uploads directory so browser can preview uploaded video clips & thumbs
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Mount static web UI
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
