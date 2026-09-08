import os
import json
import subprocess
import struct
import math

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
