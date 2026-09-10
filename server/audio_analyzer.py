import os
import json
import subprocess
import struct
import math
import re

def get_audio_info(audio_path: str) -> dict:
    """
    Extracts duration, format, sample rate, and bit rate using ffprobe.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration,bit_rate,format_name",
        "-show_entries", "stream=channels,sample_rate,codec_name",
        "-of", "json",
        audio_path
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    data = json.loads(result.stdout)
    
    fmt = data.get("format", {})
    streams = data.get("streams", [{}])
    stream0 = streams[0] if streams else {}

    duration = float(fmt.get("duration", 0.0))
    bit_rate = int(fmt.get("bit_rate", 0)) if fmt.get("bit_rate") else 192000
    sample_rate = int(stream0.get("sample_rate", 44100)) if stream0.get("sample_rate") else 44100
    channels = int(stream0.get("channels", 2)) if stream0.get("channels") else 2
    codec = stream0.get("codec_name", "unknown")

    mins = int(duration // 60)
    secs = duration % 60
    formatted_duration = f"{mins:02d}:{secs:05.2f}"

    return {
        "duration": duration,
        "formatted_duration": formatted_duration,
        "sample_rate": sample_rate,
        "channels": channels,
        "bit_rate": bit_rate,
        "codec": codec,
        "file_size": os.path.getsize(audio_path)
    }

def get_waveform_peaks(audio_path: str, num_points: int = 80) -> list[float]:
    """
    Generates normalized waveform peak heights (0.05 to 1.0) for visual timeline display.
    """
    try:
        cmd = [
            "ffmpeg",
            "-v", "error",
            "-i", audio_path,
            "-ac", "1",
            "-ar", "8000",
            "-f", "s16le",
            "-"
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        raw_data = proc.stdout
        
        total_samples = len(raw_data) // 2
        if total_samples == 0:
            return [0.2] * num_points
            
        samples = struct.unpack(f"<{total_samples}h", raw_data)
        
        chunk_size = max(1, total_samples // num_points)
        peaks = []
        for i in range(num_points):
            start = i * chunk_size
            end = min(start + chunk_size, total_samples)
            if start >= total_samples:
                peaks.append(0.1)
                continue
            chunk = samples[start:end]
            if chunk:
                rms = math.sqrt(sum(s * s for s in chunk) / len(chunk))
                peaks.append(rms)
            else:
                peaks.append(0.1)
                
        max_val = max(peaks) if peaks and max(peaks) > 0 else 1.0
        normalized = [round(max(0.08, min(1.0, p / max_val)), 3) for p in peaks]
        return normalized
    except Exception as e:
        print(f"Error extracting waveform: {e}")
        return [0.15 + 0.35 * abs(math.sin(i * 0.3)) for i in range(num_points)]

def detect_speech_silences(audio_path: str, silence_thresh_db: int = -30, min_silence_dur: float = 0.25) -> list[dict]:
    """
    Detects natural silence/pauses in speech using FFmpeg silencedetect.
    Returns list of dicts with 'start', 'end', 'midpoint'.
    """
    pauses = []
    try:
        cmd = [
            "ffmpeg", "-y",
            "-i", audio_path,
            "-af", f"silencedetect=noise={silence_thresh_db}dB:d={min_silence_dur}",
            "-f", "null",
            "-"
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines = res.stderr.splitlines()
        current_silence_start = None

        for line in lines:
            if "silence_start:" in line:
                m = re.search(r"silence_start:\s*([\d\.]+)", line)
                if m:
                    current_silence_start = float(m.group(1))
            elif "silence_end:" in line and current_silence_start is not None:
                m = re.search(r"silence_end:\s*([\d\.]+)", line)
                if m:
                    s_end = float(m.group(1))
                    mid = round((current_silence_start + s_end) / 2.0, 2)
                    pauses.append({
                        "start": current_silence_start,
                        "end": s_end,
                        "midpoint": mid,
                        "duration": round(s_end - current_silence_start, 2)
                    })
                    current_silence_start = None
    except Exception as e:
        print(f"Silence detection fallback: {e}")
    return pauses

def split_audio_into_scenes(
    audio_path: str,
    target_duration: float = 4.0,
    min_duration: float = 2.5,
    max_duration: float = 7.0
) -> list[dict]:
    """
    Intelligently partitions the audio into multiple scene intervals [start, end]
    by aligning scene cuts with natural speech pauses or rhythmic energy dips.
    Ensures every scene is between min_duration and max_duration (ideally target_duration).
    """
    info = get_audio_info(audio_path)
    total_dur = info["duration"]
    if total_dur <= 0:
        return [{"scene_index": 0, "start_time": 0.0, "end_time": 4.0, "duration": 4.0}]

    if total_dur <= max_duration:
        # Very short audio, 1 scene
        return [{
            "scene_index": 0,
            "start_time": 0.0,
            "end_time": round(total_dur, 2),
            "duration": round(total_dur, 2)
        }]

    # 1. Get natural speech pauses
    pauses = detect_speech_silences(audio_path)
    pause_midpoints = [p["midpoint"] for p in pauses if p["midpoint"] > 1.0 and p["midpoint"] < total_dur - 1.0]

    # 2. Plan cut points
    cuts = [0.0]
    current_time = 0.0

    while current_time < total_dur - min_duration:
        ideal_cut = current_time + target_duration
        if ideal_cut >= total_dur - min_duration:
            break

        # Search for a pause near ideal_cut
        candidate_pauses = [p for p in pause_midpoints if abs(p - ideal_cut) <= (max_duration - target_duration) and p > current_time + min_duration]
        if candidate_pauses:
            # Pick the closest pause to ideal_cut
            best_cut = min(candidate_pauses, key=lambda p: abs(p - ideal_cut))
        else:
            # Regular cadence cut
            best_cut = round(min(total_dur, ideal_cut), 2)

        cuts.append(best_cut)
        current_time = best_cut

    if cuts[-1] < total_dur:
        # Check if the last remaining segment is too short
        if total_dur - cuts[-1] < min_duration and len(cuts) > 1:
            cuts[-1] = round(total_dur, 2)
        else:
            cuts.append(round(total_dur, 2))

    # Construct scene objects
    scenes = []
    for i in range(len(cuts) - 1):
        s_start = cuts[i]
        s_end = cuts[i + 1]
        dur = round(s_end - s_start, 2)
        scenes.append({
            "scene_index": i,
            "start_time": s_start,
            "end_time": s_end,
            "duration": dur
        })

    return scenes
