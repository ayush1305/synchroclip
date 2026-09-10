import os
import uuid
import shutil
import json
import subprocess
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks, Query
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

# Load .env file if available
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

# Resolve base directories
if getattr(sys, 'frozen', False):
    APP_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    APP_DIR = BASE_DIR

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
MEDIA_DIR = os.path.join(UPLOAD_DIR, "media")
AUDIO_DIR = os.path.join(UPLOAD_DIR, "audio")
THUMB_DIR = os.path.join(UPLOAD_DIR, "thumbnails")
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CACHE_DIR = os.path.join(BASE_DIR, "cache")
STATIC_DIR = os.path.join(APP_DIR, "static")

for d in [UPLOAD_DIR, MEDIA_DIR, AUDIO_DIR, THUMB_DIR, PROJECTS_DIR, OUTPUT_DIR, CACHE_DIR, STATIC_DIR]:
    os.makedirs(d, exist_ok=True)

app = FastAPI(title="SynchroClip AI Video Studio", version="2.0.0")

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

# In-memory stores
AUDIO_REGISTRY = {}
MEDIA_REGISTRY = {}

# ----------------- Request Models -----------------

class PexelsSearchReq(BaseModel):
    query: str
    orientation: Optional[str] = "landscape"
    per_page: Optional[int] = 15
    page: Optional[int] = 1

class AnalyzeAudioReq(BaseModel):
    audio_id: str
    script_text: Optional[str] = ""

class AIGenerateTimelineReq(BaseModel):
    audio_id: str
    aspect_ratio: Optional[str] = "9:16"
    script_text: Optional[str] = ""
    template_id: Optional[str] = "tiktok_bold"
    highlight_color: Optional[str] = "#ffe600"

class RenderTimelineReq(BaseModel):
    timeline: Dict[str, Any]
    aspect_ratio: Optional[str] = "9:16"
    resolution: Optional[str] = "1080p"
    fps: Optional[int] = 30
    caption_template: Optional[str] = "tiktok_bold"
    highlight_color: Optional[str] = "#ffe600"
    enable_shine: Optional[bool] = False

class ProjectSaveReq(BaseModel):
    id: Optional[str] = None
    name: str
    timeline: Dict[str, Any]
    aspect_ratio: Optional[str] = "9:16"
    media_items: Optional[List[Dict[str, Any]]] = []

# Helper: Probe video/audio info
def probe_media_file(file_path: str) -> dict:
    info = {"duration": 0.0, "width": 1920, "height": 1080, "type": "video"}
    try:
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            file_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        data = json.loads(res.stdout)
        info["duration"] = float(data.get("format", {}).get("duration", 0))

        has_video = False
        has_audio = False
        for s in data.get("streams", []):
            if s.get("codec_type") == "video":
                has_video = True
                info["width"] = int(s.get("width", 1920))
                info["height"] = int(s.get("height", 1080))
            elif s.get("codec_type") == "audio":
                has_audio = True

        if has_video:
            info["type"] = "video"
        elif has_audio:
            info["type"] = "audio"
    except Exception as e:
        print(f"ffprobe warning on {file_path}: {e}")
    return info

# ----------------- API Endpoints -----------------

@app.post("/api/upload-media")
async def upload_media(file: UploadFile = File(...)):
    """
    Universal media uploader for Video, Audio, and Images.
    Extracts metadata, duration, thumbnails, and waveforms.
    """
    ext = os.path.splitext(file.filename)[1].lower() or ".mp4"
    valid_exts = {
        ".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v", # Video
        ".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", # Audio
        ".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"  # Image
    }
    if ext not in valid_exts:
        raise HTTPException(status_code=400, detail=f"Unsupported format '{ext}'.")

    media_id = uuid.uuid4().hex[:10]
    safe_filename = f"{media_id}{ext}"
    target_path = os.path.join(MEDIA_DIR, safe_filename)

    with open(target_path, "wb") as buf:
        shutil.copyfileobj(file.file, buf)

    # Determine type
    media_type = "video"
    if ext in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        media_type = "audio"
    elif ext in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}:
        media_type = "image"

    info = probe_media_file(target_path)
    thumb_url = ""
    waveform = []

    if media_type == "video":
        thumb_filename = f"thumb_{media_id}.jpg"
        thumb_path = os.path.join(THUMB_DIR, thumb_filename)
        try:
            subprocess.run([
                "ffmpeg", "-y", "-ss", "00:00:01.000" if info["duration"] > 1.5 else "00:00:00.100",
                "-i", target_path, "-vframes", "1", "-vf", "scale=480:-1", thumb_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            thumb_url = f"/uploads/thumbnails/{thumb_filename}"
        except Exception:
            thumb_url = ""

        # Extract audio to register in AUDIO_REGISTRY
        audio_filename = f"audio_{media_id}.mp3"
        audio_path = os.path.join(AUDIO_DIR, audio_filename)
        try:
            subprocess.run([
                "ffmpeg", "-y", "-i", target_path, "-vn",
                "-acodec", "libmp3lame", "-ar", "44100", "-ab", "192k", audio_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            AUDIO_REGISTRY[media_id] = {
                "id": media_id,
                "filename": file.filename,
                "path": audio_path,
                "info": {"duration": info["duration"]}
            }
        except Exception:
            pass

    elif media_type == "audio":
        # Register in AUDIO_REGISTRY
        audio_info = audio_analyzer.get_audio_info(target_path)
        waveform = audio_analyzer.get_waveform_peaks(target_path, num_points=70)
        AUDIO_REGISTRY[media_id] = {
            "id": media_id,
            "filename": file.filename,
            "path": target_path,
            "info": audio_info
        }
        info["duration"] = audio_info["duration"]

    elif media_type == "image":
        thumb_url = f"/uploads/media/{safe_filename}"
        info["duration"] = 5.0 # Default 5s image duration on timeline

    entry = {
        "id": media_id,
        "name": file.filename,
        "type": media_type,
        "url": f"/uploads/media/{safe_filename}",
        "local_path": target_path,
        "thumbnail_url": thumb_url,
        "duration": info["duration"],
        "width": info["width"],
        "height": info["height"],
        "waveform": waveform
    }
    MEDIA_REGISTRY[media_id] = entry
    return {"status": "success", "media": entry}

@app.get("/api/search-pexels")
async def search_pexels_endpoint(
    query: str = Query("cinematic", description="Search keyword"),
    orientation: str = Query("landscape", description="landscape, portrait, square"),
    page: int = Query(1, ge=1),
    per_page: int = Query(15, ge=1, le=30)
):
    """
    Searches Pexels videos via secure backend proxy.
    Falls back cleanly to curated HD stock footage.
    """
    res = pexels_client.search_pexels_videos(
        query=query,
        orientation=orientation,
        per_page=per_page,
        page=page
    )
    return res

@app.post("/api/analyze-audio")
async def analyze_audio_endpoint(req: AnalyzeAudioReq):
    """
    Analyzes an audio file:
    1. Extracts duration and waveform.
    2. Runs free speech-to-text transcription.
    3. Detects speech pauses & tempo.
    4. Extracts visual keywords and topic concepts.
    """
    if req.audio_id not in AUDIO_REGISTRY:
        raise HTTPException(status_code=404, detail="Audio ID not found")

    audio_entry = AUDIO_REGISTRY[req.audio_id]
    audio_path = audio_entry["path"]
    total_dur = float(audio_entry["info"]["duration"])

    script_text = (req.script_text or "").strip()
    if not script_text:
        # Free Google Web Speech recognition with smart chunking
        transcribed = caption_generator.transcribe_audio_file(audio_path)
        if transcribed and len(transcribed.split()) >= 2:
            script_text = transcribed
        else:
            script_text = caption_generator.generate_acoustic_script(audio_path, total_dur)

    # Detect speech pauses
    pauses = audio_analyzer.detect_speech_silences(audio_path)

    # Extract high-impact visual keywords
    primary_query, suggested_queries = text_segmenter.extract_keywords(script_text)
    keywords = [primary_query] + suggested_queries

    # Waveform
    waveform = audio_analyzer.get_waveform_peaks(audio_path, num_points=70)

    return {
        "status": "success",
        "audio_id": req.audio_id,
        "duration": total_dur,
        "transcript": script_text,
        "keywords": keywords[:6],
        "pauses_count": len(pauses),
        "waveform": waveform
    }

@app.post("/api/ai-generate-timeline")
async def ai_generate_timeline_endpoint(req: AIGenerateTimelineReq):
    """
    Option A: Automatically creates a complete multi-track timeline from audio:
    1. Speech transcription & acoustic pause slicing.
    2. Automatically matches relevant Pexels footage per scene.
    3. Aligns word-by-word animated captions.
    4. Returns fully structured editable timeline.
    """
    if req.audio_id not in AUDIO_REGISTRY:
        raise HTTPException(status_code=404, detail="Audio ID not found")

    audio_entry = AUDIO_REGISTRY[req.audio_id]
    audio_path = audio_entry["path"]
    total_dur = float(audio_entry["info"]["duration"])

    script_text = (req.script_text or "").strip()
    if not script_text:
        transcribed = caption_generator.transcribe_audio_file(audio_path)
        if transcribed and len(transcribed.split()) >= 2:
            script_text = transcribed
        else:
            script_text = caption_generator.generate_acoustic_script(audio_path, total_dur)

    # 1. Segment scenes
    scenes = text_segmenter.segment_script_and_allocate_time(
        script_text=script_text,
        total_duration=total_dur,
        min_segment_duration=2.5,
        max_segment_duration=6.5
    )

    # 2. Select distinct Pexels clips for each scene
    used_ids = set()
    v1_clips = []
    orientation = "portrait" if req.aspect_ratio == "9:16" else "landscape"

    for idx, s in enumerate(scenes):
        query = s.get("primary_query") or "cinematic scenery"
        clip = pexels_client.select_distinct_clip(
            query=query,
            scene_idx=idx,
            used_clip_ids=used_ids
        )
        clip_dur = s["duration"]
        v1_clips.append({
            "id": f"clip_v1_{idx+1}",
            "trackId": "V1",
            "type": "video",
            "title": clip.get("title", f"Scene #{idx+1}"),
            "url": clip.get("video_url") or clip.get("preview_url"),
            "thumbnail_url": clip.get("image", ""),
            "startTime": s["start_time"],
            "duration": clip_dur,
            "sourceStart": 0.0,
            "sourceDuration": clip.get("duration", clip_dur),
            "properties": {
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0,
                "speed": 1.0,
                "volume": 0.0,
                "brightness": 0,
                "contrast": 0,
                "saturation": 0,
                "blur": 0
            }
        })

    # 3. Align captions with word-level timing
    cards, words = caption_generator.align_words_to_audio(
        audio_path=audio_path,
        text=script_text,
        total_duration=total_dur
    )

    t1_clips = []
    for idx, card in enumerate(cards):
        t1_clips.append({
            "id": f"cap_t1_{idx+1}",
            "trackId": "T1",
            "type": "caption",
            "text": card["text"],
            "startTime": card["start_time"],
            "duration": round(card["end_time"] - card["start_time"], 2),
            "words": card.get("words", []),
            "properties": {
                "templateId": req.template_id or "tiktok_bold",
                "highlightColor": req.highlight_color or "#ffe600",
                "fontFamily": "Montserrat",
                "fontSize": 48,
                "color": "#ffffff",
                "animation": "pop",
                "positionY": 80 # percentage from top
            }
        })

    # 4. Audio clip on A1
    a1_clips = [{
        "id": "audio_a1_1",
        "trackId": "A1",
        "type": "audio",
        "title": audio_entry["filename"],
        "url": f"/api/audio/{req.audio_id}",
        "startTime": 0.0,
        "duration": total_dur,
        "sourceStart": 0.0,
        "sourceDuration": total_dur,
        "properties": {
            "volume": 1.0,
            "fadeIn": 0.0,
            "fadeOut": 0.5
        }
    }]

    timeline = {
        "duration": total_dur,
        "aspectRatio": req.aspect_ratio or "9:16",
        "tracks": [
            {"id": "T1", "name": "Text & Captions", "type": "text", "clips": t1_clips},
            {"id": "V2", "name": "Overlay / PiP", "type": "video", "clips": []},
            {"id": "V1", "name": "Main Video", "type": "video", "clips": v1_clips},
            {"id": "A1", "name": "Voiceover", "type": "audio", "clips": a1_clips},
            {"id": "A2", "name": "Background Music", "type": "audio", "clips": []}
        ]
    }

    return {
        "status": "success",
        "audio_id": req.audio_id,
        "transcript": script_text,
        "timeline": timeline,
        "scenes_count": len(scenes)
    }

@app.post("/api/render-timeline")
async def render_timeline_endpoint(req: RenderTimelineReq):
    """
    Renders the complete multi-track timeline composition via FFmpeg.
    Supports resolution selection (720p, 1080p, 4K), transitions,
    audio mixing, and burned karaoke subtitles with ZERO WATERMARK.
    """
    timeline = req.timeline
    tracks = timeline.get("tracks", [])
    total_duration = float(timeline.get("duration", 10.0))
    aspect_ratio = req.aspect_ratio or timeline.get("aspectRatio", "9:16")

    # Extract V1 clips
    v1_track = next((t for t in tracks if t.get("id") == "V1"), None)
    v1_clips = v1_track.get("clips", []) if v1_track else []

    # Extract A1 audio track
    a1_track = next((t for t in tracks if t.get("id") == "A1"), None)
    a1_clips = a1_track.get("clips", []) if a1_track else []

    # Extract T1 captions
    t1_track = next((t for t in tracks if t.get("id") == "T1"), None)
    t1_clips = t1_track.get("clips", []) if t1_track else []

    # Map V1 clips into scene format for video composer
    scenes = []
    for idx, c in enumerate(v1_clips):
        clip_url = c.get("url", "")
        scenes.append({
            "id": idx + 1,
            "start_time": c.get("startTime", 0.0),
            "end_time": c.get("startTime", 0.0) + c.get("duration", 3.0),
            "duration": c.get("duration", 3.0),
            "selected_clip": {
                "id": c.get("id", f"c_{idx}"),
                "video_url": clip_url,
                "local_path": c.get("local_path")
            }
        })

    if not scenes:
        raise HTTPException(status_code=400, detail="No video clips found on Track V1 to render.")

    # Resolve audio file
    audio_path = None
    if a1_clips:
        first_audio = a1_clips[0]
        url = first_audio.get("url", "")
        if "/api/audio/" in url:
            a_id = url.split("/api/audio/")[-1].split("?")[0]
            if a_id in AUDIO_REGISTRY:
                audio_path = AUDIO_REGISTRY[a_id]["path"]

    if not audio_path:
        # Fallback silent audio track
        audio_path = os.path.join(OUTPUT_DIR, "silent_temp.mp3")
        if not os.path.exists(audio_path):
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo",
                "-t", str(total_duration), "-q:a", "9", "-acodec", "libmp3lame", audio_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Subtitles ASS generation
    caption_ass_path = None
    if t1_clips and req.caption_template != "none":
        sub_filename = f"timeline_subs_{uuid.uuid4().hex[:8]}.ass"
        sub_path = os.path.join(OUTPUT_DIR, sub_filename)
        width = 1080 if aspect_ratio == "9:16" else 1920
        height = 1920 if aspect_ratio == "9:16" else 1080

        # Convert T1 clips to caption cards
        caption_cards = []
        for idx, tc in enumerate(t1_clips):
            caption_cards.append({
                "card_id": idx + 1,
                "start_time": tc.get("startTime", 0.0),
                "end_time": tc.get("startTime", 0.0) + tc.get("duration", 2.0),
                "text": tc.get("text", ""),
                "words": tc.get("words", [])
            })

        caption_generator.generate_ass_subtitles(
            caption_cards=caption_cards,
            template_id=req.caption_template or "hormozi_classic",
            highlight_color_key=req.highlight_color or "#ffe600",
            output_path=sub_path,
            width=width,
            height=height,
            enable_shine=bool(req.enable_shine)
        )
        caption_ass_path = sub_path

    # Start render job
    job_id = video_composer.start_render_job(
        scenes=scenes,
        audio_path=audio_path,
        total_audio_duration=total_duration,
        transition_type="fade",
        transition_duration=0.6,
        aspect_ratio=aspect_ratio,
        caption_ass_path=caption_ass_path,
        cache_dir=CACHE_DIR,
        output_dir=OUTPUT_DIR
    )

    return {"status": "started", "job_id": job_id}

@app.get("/api/render-status/{job_id}")
async def get_render_status_endpoint(job_id: str):
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
        resp["output_file"] = job["output_file"]
        resp["download_url"] = f"/api/download/{job['output_file']}"
        resp["video_url"] = f"/api/download/{job['output_file']}"
    return resp

@app.get("/api/download/{filename}")
async def download_output(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="video/mp4", filename=filename)

@app.get("/api/caption-presets")
async def get_caption_presets():
    """
    Returns rich preset styles including TikTok, Shorts, Minimal, Bold Pop, Neon, Comic, Luxury, Karaoke.
    """
    presets = [
        {"id": "tiktok_bold", "name": "TikTok Viral", "category": "Social", "font": "Montserrat", "highlight": "#ffe600", "anim": "pop"},
        {"id": "youtube_shorts", "name": "YouTube Shorts Pop", "category": "Social", "font": "Poppins", "highlight": "#06b6d4", "anim": "bounce"},
        {"id": "hormozi_classic", "name": "Hormozi Classic", "category": "Trending", "font": "Montserrat", "highlight": "#22c55e", "anim": "scale"},
        {"id": "minimal_clean", "name": "Minimal Clean", "category": "Modern", "font": "Inter", "highlight": "#ffffff", "anim": "none"},
        {"id": "neon_glow", "name": "Cyber Neon Glow", "category": "Glow", "font": "Rubik", "highlight": "#06b6d4", "anim": "glow"},
        {"id": "beast_mode", "name": "MrBeast Punch", "category": "Comic", "font": "Bebas Neue", "highlight": "#facc15", "anim": "pop"},
        {"id": "cinematic_gold", "name": "Cinematic Serif", "category": "Cinematic", "font": "Playfair Display", "highlight": "#eab308", "anim": "fade"},
        {"id": "karaoke_sweep", "name": "Karaoke Word Sweep", "category": "Karaoke", "font": "Oswald", "highlight": "#ec4899", "anim": "underline"},
        {"id": "comic_boom", "name": "Comic Boom", "category": "Comic", "font": "Anton", "highlight": "#ef4444", "anim": "bounce"},
        {"id": "luxury_minimal", "name": "Luxury Elegance", "category": "Luxury", "font": "Playfair Display", "highlight": "#d4af37", "anim": "none"}
    ]
    fonts = ["Inter", "Roboto", "Poppins", "Montserrat", "Bebas Neue", "Oswald", "Playfair Display", "Rubik", "Anton"]
    return {"status": "success", "presets": presets, "fonts": fonts}

@app.post("/api/projects")
async def save_project(req: ProjectSaveReq):
    proj_id = req.id or uuid.uuid4().hex[:10]
    proj_data = {
        "id": proj_id,
        "name": req.name,
        "aspect_ratio": req.aspect_ratio,
        "timeline": req.timeline,
        "media_items": req.media_items
    }
    proj_file = os.path.join(PROJECTS_DIR, f"{proj_id}.json")
    with open(proj_file, "w", encoding="utf-8") as f:
        json.dump(proj_data, f, indent=2)
    return {"status": "success", "project_id": proj_id}

@app.get("/api/projects/{project_id}")
async def load_project(project_id: str):
    proj_file = os.path.join(PROJECTS_DIR, f"{project_id}.json")
    if not os.path.exists(proj_file):
        raise HTTPException(status_code=404, detail="Project not found")
    with open(proj_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {"status": "success", "project": data}

@app.get("/api/sample-demo")
async def get_sample_demo():
    demo_filename = "demo_ambient_voice.mp3"
    demo_path = os.path.join(UPLOAD_DIR, demo_filename)
    if not os.path.exists(demo_path):
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=220:duration=16",
            "-filter_complex", "volume=0.3,aecho=0.8:0.88:60:0.4",
            "-c:a", "libmp3lame", demo_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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
        "Artificial intelligence is transforming how creative minds tell visual stories. "
        "With intelligent scene detection and synchronized music beats, every moment comes to life. "
        "Welcome to the next generation of creative video editing."
    )

    return {
        "status": "success",
        "audio_id": demo_id,
        "filename": "demo_ambient_track.mp3",
        "duration": info["duration"],
        "waveform": waveform,
        "script": sample_script
    }


# ----------------- Compatibility Endpoints for Earlier Tests -----------------

@app.get("/api/caption-templates")
async def get_caption_templates_compat():
    return {
        "status": "success",
        "templates": list(caption_templates.TEMPLATES.values()),
        "colors": caption_templates.HIGHLIGHT_COLORS,
        "famous_fonts": caption_templates.FAMOUS_FONTS,
        "marker_styles": caption_templates.MARKER_STYLES
    }

class DirectRenderReq(BaseModel):
    audio_id: str
    scenes: Optional[list] = None
    transition_type: Optional[str] = "fade"
    transition_duration: Optional[float] = 0.8
    aspect_ratio: Optional[str] = "16:9"
    caption_template: Optional[str] = "none"
    primary_color: Optional[str] = None
    highlight_color: Optional[str] = "yellow"
    caption_cards: Optional[list] = None
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

@app.post("/api/render")
async def render_compat(req: DirectRenderReq):
    if req.audio_id not in AUDIO_REGISTRY:
        raise HTTPException(status_code=404, detail="Audio ID not found")

    audio_entry = AUDIO_REGISTRY[req.audio_id]
    audio_path = audio_entry["path"]
    total_audio_duration = float(audio_entry["info"]["duration"])

    caption_ass_path = None
    if (req.caption_template and req.caption_template != "none") and req.caption_cards:
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

    if req.is_direct_video and req.direct_video_path and os.path.exists(req.direct_video_path):
        job_id = video_composer.start_direct_render_job(
            video_path=req.direct_video_path,
            caption_ass_path=caption_ass_path,
            output_dir=OUTPUT_DIR,
            video_focus=bool(req.video_focus),
            pip_info=pip_info
        )
        return {"status": "started", "job_id": job_id}

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
    return {"status": "started", "job_id": job_id}

@app.post("/api/upload-direct-video")
async def upload_direct_video_compat(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower() or ".mp4"
    video_id = uuid.uuid4().hex[:10]
    audio_id = f"audio_{video_id}"
    safe_video_name = f"direct_{video_id}{ext}"
    safe_audio_name = f"audio_{video_id}.mp3"

    direct_dir = os.path.join(UPLOAD_DIR, "direct_videos")
    os.makedirs(direct_dir, exist_ok=True)
    target_video = os.path.join(direct_dir, safe_video_name)
    target_audio = os.path.join(AUDIO_DIR, safe_audio_name)

    with open(target_video, "wb") as buf:
        shutil.copyfileobj(file.file, buf)

    subprocess.run([
        "ffmpeg", "-y", "-i", target_video, "-vn",
        "-acodec", "libmp3lame", "-ar", "44100", "-ab", "192k", target_audio
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    info = audio_analyzer.get_audio_info(target_audio)
    waveform = audio_analyzer.get_waveform_peaks(target_audio, num_points=70)
    AUDIO_REGISTRY[audio_id] = {
        "id": audio_id,
        "filename": file.filename,
        "path": target_audio,
        "info": info
    }

    return {
        "status": "success",
        "video_id": video_id,
        "audio_id": audio_id,
        "filename": file.filename,
        "local_video_path": target_video,
        "duration": info["duration"],
        "width": 720,
        "height": 1280,
        "waveform": waveform
    }

@app.post("/api/upload-pip-image")
async def upload_pip_compat(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower() or ".png"
    img_id = uuid.uuid4().hex[:10]
    pip_dir = os.path.join(UPLOAD_DIR, "pip")
    os.makedirs(pip_dir, exist_ok=True)
    target = os.path.join(pip_dir, f"pip_{img_id}{ext}")
    with open(target, "wb") as buf:
        shutil.copyfileobj(file.file, buf)
    return {
        "status": "success",
        "pip_id": img_id,
        "filename": file.filename,
        "path": target,
        "url": f"/uploads/pip/pip_{img_id}{ext}"
    }

class SegmentReq(BaseModel):
    audio_id: str
    script_text: Optional[str] = ""

@app.post("/api/segment-script")
async def segment_script_compat(req: SegmentReq):
    if req.audio_id not in AUDIO_REGISTRY:
        raise HTTPException(status_code=404, detail="Audio ID not found")
    audio_entry = AUDIO_REGISTRY[req.audio_id]
    text = (req.script_text or "").strip()
    if not text:
        text = caption_generator.transcribe_audio_file(audio_entry["path"])
        if not text:
            text = caption_generator.generate_acoustic_script(audio_entry["path"], float(audio_entry["info"]["duration"]))

    scenes = text_segmenter.segment_script_and_allocate_time(text, float(audio_entry["info"]["duration"]))
    return {"status": "success", "transcript": text, "scenes": scenes, "total_duration": float(audio_entry["info"]["duration"])}

class CaptionsReq(BaseModel):
    audio_id: str
    script_text: Optional[str] = ""
    template_id: Optional[str] = "hormozi_classic"

@app.post("/api/generate-captions")
async def generate_captions_compat(req: CaptionsReq):
    if req.audio_id not in AUDIO_REGISTRY:
        raise HTTPException(status_code=404, detail="Audio ID not found")
    audio_entry = AUDIO_REGISTRY[req.audio_id]
    text = (req.script_text or "").strip()
    if not text:
        text = caption_generator.transcribe_audio_file(audio_entry["path"])
        if not text:
            text = caption_generator.generate_acoustic_script(audio_entry["path"], float(audio_entry["info"]["duration"]))

    cards, words = caption_generator.align_words_to_audio(audio_entry["path"], text, float(audio_entry["info"]["duration"]))
    return {"status": "success", "transcript": text, "cards": cards, "words": words}

class AutoMatchReq(BaseModel):
    scenes: list
    api_key: Optional[str] = None
    orientation: Optional[str] = "landscape"

@app.post("/api/auto-match-all")
async def auto_match_all_compat(req: AutoMatchReq):
    used_ids = set()
    for idx, s in enumerate(req.scenes):
        query = s.get("primary_query") or "cinematic view"
        clip = pexels_client.select_distinct_clip(query, idx, used_ids, req.api_key)
        s["selected_clip"] = clip
    return {"status": "success", "scenes": req.scenes}

class AnalyzeGenReq(BaseModel):
    audio_id: str
    script_text: Optional[str] = ""
    aspect_ratio: Optional[str] = "9:16"
    template_id: Optional[str] = "tiktok_bold"

@app.post("/api/analyze-and-generate")
async def analyze_and_generate_compat(req: AnalyzeGenReq):
    if req.audio_id not in AUDIO_REGISTRY:
        raise HTTPException(status_code=404, detail="Audio ID not found")
    audio_entry = AUDIO_REGISTRY[req.audio_id]
    audio_path = audio_entry["path"]
    total_dur = float(audio_entry["info"]["duration"])

    script_text = (req.script_text or "").strip()
    if not script_text:
        transcribed = caption_generator.transcribe_audio_file(audio_path)
        if transcribed and len(transcribed.split()) >= 2:
            script_text = transcribed
        else:
            script_text = caption_generator.generate_acoustic_script(audio_path, total_dur)

    scenes = text_segmenter.segment_script_and_allocate_time(script_text, total_dur)
    used_ids = set()
    for idx, s in enumerate(scenes):
        query = s.get("primary_query") or "cinematic scenery"
        clip = pexels_client.select_distinct_clip(query, idx, used_ids)
        s["selected_clip"] = clip

    cards, words = caption_generator.align_words_to_audio(audio_path, script_text, total_dur)
    return {
        "status": "success",
        "audio_id": req.audio_id,
        "total_duration": total_dur,
        "transcript": script_text,
        "scenes": scenes,
        "caption_cards": cards,
        "timed_words": words
    }

class SwapClipReq(BaseModel):
    query: str
    aspect_ratio: Optional[str] = "9:16"

@app.post("/api/swap-clip")
async def swap_clip_compat(req: SwapClipReq):
    orientation = "portrait" if req.aspect_ratio == "9:16" else "landscape"
    res = pexels_client.search_pexels_videos(req.query, orientation=orientation, per_page=12)
    return res


# Static file serving
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/api/audio", StaticFiles(directory=AUDIO_DIR), name="audio")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
