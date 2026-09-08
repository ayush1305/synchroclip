import os
import re
import time
import uuid
import urllib.request
import subprocess
import threading
from typing import Callable, Optional

# Active job tracking
RENDER_JOBS = {}

def download_file(url: str, dest_path: str, progress_cb: Optional[Callable[[float], None]] = None) -> str:
    """
    Downloads a remote file with caching and progress reporting.
    """
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        return dest_path

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    temp_path = dest_path + ".tmp"

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=30) as response, open(temp_path, "wb") as out_file:
            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            chunk_size = 1024 * 512  # 512KB

            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                out_file.write(chunk)
                downloaded += len(chunk)
                if total_size > 0 and progress_cb:
                    progress_cb(min(1.0, downloaded / total_size))

        if os.path.exists(dest_path):
            os.remove(dest_path)
        os.rename(temp_path, dest_path)
        return dest_path
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

def render_video_task(
    job_id: str,
    scenes: list[dict],
    audio_path: str,
    total_audio_duration: float,
    transition_type: str = "fade",
    transition_duration: float = 0.8,
    aspect_ratio: str = "16:9",
    caption_ass_path: Optional[str] = None,
    cache_dir: str = "cache",
    output_dir: str = "output"
):
    """
    Background worker that downloads clips, builds the FFmpeg filter graph,
    stitches clips with smooth transitions, muxes audio, and tracks progress.
    """
    try:
        RENDER_JOBS[job_id]["status"] = "downloading"
        RENDER_JOBS[job_id]["progress"] = 5
        RENDER_JOBS[job_id]["message"] = "Preparing and downloading stock footage..."

        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        # 1. Download/resolve local paths for each scene's clip
        clip_paths = []
        num_scenes = len(scenes)
        
        for i, scene in enumerate(scenes):
            clip_info = scene.get("selected_clip")
            if not clip_info or not clip_info.get("video_url"):
                raise ValueError(f"Scene #{scene.get('id', i+1)} has no video clip selected.")

            url = clip_info["video_url"]
            ext = "mp4"
            clip_filename = f"clip_{clip_info.get('id', uuid.uuid4().hex[:8])}.{ext}"
            local_clip_path = os.path.join(cache_dir, clip_filename)

            def make_dl_cb(scene_idx):
                return lambda p: RENDER_JOBS[job_id].update({
                    "progress": int(5 + (scene_idx + p) / num_scenes * 25),
                    "message": f"Downloading clip {scene_idx + 1} of {num_scenes}..."
                })

            if url.startswith("http://") or url.startswith("https://"):
                download_file(url, local_clip_path, make_dl_cb(i))
            else:
                local_clip_path = url

            clip_paths.append(local_clip_path)

        RENDER_JOBS[job_id]["status"] = "composing"
        RENDER_JOBS[job_id]["progress"] = 35
        RENDER_JOBS[job_id]["message"] = "Composing transition timeline..."

        # 2. Dimensions based on aspect ratio
        if aspect_ratio == "9:16":
            target_width = 1080
            target_height = 1920
        else: # 16:9 default
            target_width = 1920
            target_height = 1080

        # Validate transition duration
        t_dur = min(1.5, max(0.3, float(transition_duration)))
        # Map friendly name to FFmpeg xfade transition
        valid_transitions = {
            "fade": "fade",
            "dissolve": "dissolve",
            "fadeblack": "fadeblack",
            "fadewhite": "fadewhite",
            "wipeleft": "wipeleft",
            "wiperight": "wiperight",
            "smoothleft": "smoothleft",
            "circlecrop": "circlecrop",
            "hlslice": "hlslice",
            "radial": "radial"
        }
        xfade_trans = valid_transitions.get(transition_type.lower(), "fade")

        # 3. Calculate trimmed durations for each clip
        # Scene i visible duration = scenes[i]["duration"]
        # Clip 0 needs length: D_0
        # Clip i (i >= 1) needs length: D_i + t_dur
        durations = [float(s["duration"]) for s in scenes]

        # Check for caption ASS file
        has_captions = False
        safe_ass_filter = ""
        if caption_ass_path and os.path.exists(caption_ass_path) and os.path.getsize(caption_ass_path) > 30:
            formatted_ass = os.path.abspath(caption_ass_path).replace("\\", "/").replace(":", "\\:")
            safe_ass_filter = f"ass='{formatted_ass}'"
            has_captions = True

        # In case of 1 clip:
        if num_scenes == 1:
            output_filename = f"export_{job_id}.mp4"
            output_path = os.path.join(output_dir, output_filename)
            
            vf_chain = [
                f"scale={target_width}:{target_height}:force_original_aspect_ratio=increase",
                f"crop={target_width}:{target_height}",
                "setsar=1,fps=30,format=yuv420p",
                "eq=contrast=1.04:saturation=1.05"
            ]
            if has_captions:
                vf_chain.append(safe_ass_filter)

            cmd = [
                "ffmpeg", "-y",
                "-stream_loop", "-1",
                "-i", clip_paths[0],
                "-i", audio_path,
                "-vf", ",".join(vf_chain),
                "-c:v", "libx264", "-preset", "fast", "-crf", "21",
                "-c:a", "aac", "-b:a", "192k",
                "-t", str(durations[0]),
                output_path
            ]
            
            RENDER_JOBS[job_id]["status"] = "rendering"
            RENDER_JOBS[job_id]["progress"] = 50
            subprocess.run(cmd, check=True)
            
            RENDER_JOBS[job_id]["status"] = "done"
            RENDER_JOBS[job_id]["progress"] = 100
            RENDER_JOBS[job_id]["message"] = "Rendering complete!"
            RENDER_JOBS[job_id]["output_file"] = output_filename
            return

        # 4. Build FFmpeg command with filter_complex and xfade chain
        # Inputs:
        # -stream_loop -1 -i clip_paths[i] (trimmed to required duration)
        # Plus the last input is user audio
        input_args = []
        filter_parts = []

        for i, path in enumerate(clip_paths):
            needed_dur = durations[0] if i == 0 else (durations[i] + t_dur)
            input_args.extend([
                "-stream_loop", "-1",
                "-t", f"{needed_dur + 0.5:.3f}",
                "-i", path
            ])
            
            # Format and normalize each video stream
            norm_filter = (
                f"[{i}:v]scale={target_width}:{target_height}:force_original_aspect_ratio=increase,"
                f"crop={target_width}:{target_height},"
                f"setsar=1,fps=30,format=yuv420p,"
                f"eq=contrast=1.04:saturation=1.05[v{i}]"
            )
            filter_parts.append(norm_filter)

        # Audio input index
        audio_input_idx = len(clip_paths)
        input_args.extend(["-i", audio_path])

        # Build xfade chain
        # Offset for transition k: (sum_{j=0}^{k-1} D_j) - t_dur
        current_sum = durations[0]
        prev_link = "v0"

        for k in range(1, num_scenes):
            offset = current_sum - t_dur
            next_link = f"v{k}"
            out_link = f"xf{k}" if k < num_scenes - 1 else "vxfaded"
            
            xfade_filter = (
                f"[{prev_link}][{next_link}]xfade=transition={xfade_trans}:"
                f"duration={t_dur:.2f}:offset={offset:.3f}[{out_link}]"
            )
            filter_parts.append(xfade_filter)
            
            current_sum += durations[k]
            prev_link = out_link

        # If captions are enabled, attach ass filter to last video link
        final_video_label = "vfinal"
        if has_captions:
            filter_parts.append(f"[{prev_link}]{safe_ass_filter}[vfinal]")
        else:
            filter_parts.append(f"[{prev_link}]null[vfinal]")

        filter_complex_str = ";".join(filter_parts)

        output_filename = f"export_{job_id}.mp4"
        output_path = os.path.join(output_dir, output_filename)

        full_cmd = [
            "ffmpeg", "-y",
            *input_args,
            "-filter_complex", filter_complex_str,
            "-map", f"[{final_video_label}]",
            "-map", f"{audio_input_idx}:a",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "21",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", f"{total_audio_duration:.3f}",
            "-progress", "pipe:1",
            output_path
        ]

        RENDER_JOBS[job_id]["status"] = "rendering"
        RENDER_JOBS[job_id]["progress"] = 40
        RENDER_JOBS[job_id]["message"] = "Rendering seamless cinematic video..."

        log_file_path = os.path.join(output_dir, f"render_{job_id}.log")
        with open(log_file_path, "w", encoding="utf-8") as err_log:
            proc = subprocess.Popen(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=err_log,
                text=True,
                bufsize=1
            )

            # Monitor stdout for progress
            time_regex = re.compile(r"out_time_us=(\d+)")
            while True:
                line = proc.stdout.readline()
                if not line and proc.poll() is not None:
                    break
                if line:
                    m = time_regex.search(line)
                    if m:
                        current_us = int(m.group(1))
                        current_sec = current_us / 1000000.0
                        prog = min(98, 40 + int((current_sec / max(1.0, total_audio_duration)) * 58))
                        RENDER_JOBS[job_id]["progress"] = prog
                        RENDER_JOBS[job_id]["message"] = f"Rendering transitions ({prog}%)..."

            rc = proc.wait()

        if rc != 0:
            err_content = ""
            if os.path.exists(log_file_path):
                with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
                    err_content = f.read()[-300:]
            print(f"FFmpeg error:\n{err_content}")
            RENDER_JOBS[job_id]["status"] = "error"
            RENDER_JOBS[job_id]["message"] = f"Video encoding error: {err_content}"
            return

        RENDER_JOBS[job_id]["status"] = "done"
        RENDER_JOBS[job_id]["progress"] = 100
        RENDER_JOBS[job_id]["message"] = "Video generated successfully!"
        RENDER_JOBS[job_id]["output_file"] = output_filename

    except Exception as e:
        print(f"Render job {job_id} error: {e}")
        RENDER_JOBS[job_id]["status"] = "error"
        RENDER_JOBS[job_id]["message"] = str(e)

def start_render_job(
    scenes: list[dict],
    audio_path: str,
    total_audio_duration: float,
    transition_type: str = "fade",
    transition_duration: float = 0.8,
    aspect_ratio: str = "16:9",
    caption_ass_path: Optional[str] = None,
    cache_dir: str = "cache",
    output_dir: str = "output"
) -> str:
    """
    Creates and initiates a background render job.
    """
    job_id = uuid.uuid4().hex[:12]
    RENDER_JOBS[job_id] = {
        "id": job_id,
        "status": "queued",
        "progress": 0,
        "message": "Initializing video render pipeline...",
        "output_file": None,
        "created_at": time.time()
    }

    t = threading.Thread(
        target=render_video_task,
        args=(
            job_id,
            scenes,
            audio_path,
            total_audio_duration,
            transition_type,
            transition_duration,
            aspect_ratio,
            caption_ass_path,
            cache_dir,
            output_dir
        ),
        daemon=True
    )
    t.start()
    return job_id
