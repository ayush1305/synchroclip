import os
import re
import math
import subprocess
import speech_recognition as sr
from typing import Optional
import caption_templates

def detect_speech_intervals(audio_path: str, total_duration: float) -> list[tuple[float, float]]:
    """
    Uses ffmpeg silencedetect to find active speech intervals in audio.
    """
    cmd = [
        "ffmpeg", "-i", audio_path,
        "-af", "silencedetect=noise=-30dB:d=0.25",
        "-f", "null", "-"
    ]
    try:
        proc = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
        lines = proc.stderr.split("\n")
        
        silence_starts = []
        silence_ends = []
        for line in lines:
            if "silence_start:" in line:
                m = re.search(r"silence_start:\s*([0-9.]+)", line)
                if m:
                    silence_starts.append(float(m.group(1)))
            elif "silence_end:" in line:
                m = re.search(r"silence_end:\s*([0-9.]+)", line)
                if m:
                    silence_ends.append(float(m.group(1)))

        if not silence_starts:
            # Whole audio is one speech interval
            return [(0.2, max(0.5, total_duration - 0.2))]

        speech_intervals = []
        cur_pos = 0.1
        for start, end in zip(silence_starts, silence_ends):
            if start > cur_pos + 0.3:
                speech_intervals.append((cur_pos, start))
            cur_pos = end

        if cur_pos < total_duration - 0.3:
            speech_intervals.append((cur_pos, total_duration - 0.2))

        return speech_intervals if speech_intervals else [(0.2, total_duration - 0.2)]
    except Exception as e:
        print(f"Silencedetect error: {e}")
        return [(0.2, max(0.5, total_duration - 0.2))]

def transcribe_audio_file(audio_path: str) -> str:
    """
    Transcribes audio using SpeechRecognition and Google Web Speech API.
    Converts audio to temporary WAV for recognition if needed.
    """
    recognizer = sr.Recognizer()
    temp_wav = audio_path + ".temp.wav"
    
    try:
        # Convert to 16kHz mono wav
        cmd = [
            "ffmpeg", "-y",
            "-i", audio_path,
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            temp_wav
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        with sr.AudioFile(temp_wav) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except Exception as e:
        print(f"Speech recognition notice: {e}")
        return ""
    finally:
        if os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except Exception:
                pass

def align_words_to_timeline(
    script_text: str,
    audio_path: str,
    total_duration: float
) -> list[dict]:
    """
    Aligns words in the script to the audio duration with speech pacing.
    """
    # Clean words
    words = re.findall(r"\b[\w']+\b", script_text)
    if not words:
        words = ["DISCOVER", "THE", "FUTURE", "TODAY"]

    # Detect speech active intervals
    speech_intervals = detect_speech_intervals(audio_path, total_duration)
    total_speech_time = sum(end - start for start, end in speech_intervals)
    if total_speech_time <= 0:
        total_speech_time = total_duration

    # Word weight based on length / syllables
    weights = [max(1, len(w)) for w in words]
    total_weight = sum(weights)

    timed_words = []
    # Distribute words across speech intervals
    word_idx = 0
    num_words = len(words)

    for interval_start, interval_end in speech_intervals:
        if word_idx >= num_words:
            break

        interval_dur = interval_end - interval_start
        # Proportion of remaining words for this interval
        interval_share = interval_dur / total_speech_time
        words_in_this_interval = max(1, round(num_words * interval_share))
        
        # Don't exceed available words
        words_to_take = min(words_in_this_interval, num_words - word_idx)
        if interval_start == speech_intervals[-1][0]:
            # Take all remaining words on last interval
            words_to_take = num_words - word_idx

        sub_words = words[word_idx:word_idx + words_to_take]
        sub_weights = weights[word_idx:word_idx + words_to_take]
        sub_total_weight = sum(sub_weights) if sum(sub_weights) > 0 else 1

        cur_t = interval_start
        for w, wt in zip(sub_words, sub_weights):
            w_dur = (wt / sub_total_weight) * interval_dur
            w_start = round(cur_t, 2)
            w_end = round(cur_t + w_dur, 2)
            cur_t = w_end

            timed_words.append({
                "word": w.upper(),
                "start": w_start,
                "end": w_end,
                "duration": round(w_dur, 2)
            })

        word_idx += words_to_take

    return timed_words

def chunk_words_into_cards(
    timed_words: list[dict],
    is_word_pop: bool = False,
    max_words_per_card: int = 4
) -> list[dict]:
    """
    Groups words into caption display cards (e.g. 3-4 words per card, or 1 word for word_pop).
    """
    if is_word_pop:
        chunk_size = 1
    else:
        chunk_size = max_words_per_card

    cards = []
    card_id = 1
    for i in range(0, len(timed_words), chunk_size):
        chunk = timed_words[i:i + chunk_size]
        card_start = chunk[0]["start"]
        card_end = chunk[-1]["end"]

        cards.append({
            "card_id": card_id,
            "start_time": card_start,
            "end_time": card_end,
            "formatted_time": f"{to_ass_time(card_start)} - {to_ass_time(card_end)}",
            "text": " ".join(w["word"] for w in chunk),
            "words": chunk
        })
        card_id += 1

    return cards

def to_ass_time(seconds: float) -> str:
    """
    Converts seconds float to ASS timestamp: H:MM:SS.cs (centiseconds).
    """
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100)) % 100
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def generate_ass_subtitles(
    caption_cards: list[dict],
    template_id: str = "capcut_classic",
    highlight_color_key: str = "yellow",
    output_path: str = "captions.ass",
    width: int = 1920,
    height: int = 1080
) -> str:
    """
    Generates Advanced SubStation Alpha (.ass) subtitle file with word-by-word
    karaoke highlighting and motion graphics matching the chosen template.
    """
    tpl = caption_templates.get_template(template_id)
    if tpl["id"] == "none":
        # Create empty dummy file or return empty
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("")
        return output_path

    header = caption_templates.build_ass_header(template_id, width=width, height=height)
    
    # Highlight color ASS tag
    color_info = caption_templates.HIGHLIGHT_COLORS.get(highlight_color_key, caption_templates.HIGHLIGHT_COLORS["yellow"])
    highlight_ass = color_info["ass"]
    primary_ass = tpl["primary_color"]

    events = []

    for card in caption_cards:
        words = card["words"]
        if not words:
            continue

        # For each word in this card, generate a dialogue slice during which that word is highlighted
        for target_idx, active_word in enumerate(words):
            slice_start = to_ass_time(active_word["start"])
            slice_end = to_ass_time(active_word["end"])

            # Build line text with active word highlighted
            line_parts = []
            for idx, w in enumerate(words):
                word_text = w["word"]
                if idx == target_idx:
                    # Active word: pop scale + active highlight color
                    if tpl["animation"] == "bounce":
                        line_parts.append(f"{{\\c{highlight_ass}\\fscx112\\fscy112}}{word_text}{{\\r}}")
                    elif tpl["animation"] == "word_zoom":
                        line_parts.append(f"{{\\c{highlight_ass}\\fscx120\\fscy120}}{word_text}{{\\r}}")
                    elif tpl["animation"] == "glow_pulse":
                        line_parts.append(f"{{\\c{highlight_ass}\\bord5\\blur4}}{word_text}{{\\r}}")
                    elif tpl["animation"] == "fire_pulse":
                        line_parts.append(f"{{\\c{highlight_ass}\\bord6\\3c&H000000FF&}}{word_text}{{\\r}}")
                    else:
                        line_parts.append(f"{{\\c{highlight_ass}}}{word_text}{{\\r}}")
                else:
                    # Inactive word
                    line_parts.append(f"{{\\c{primary_ass}}}{word_text}")

            line_text = " ".join(line_parts)
            dialogue_line = f"Dialogue: 0,{slice_start},{slice_end},Default,,0,0,0,,{line_text}"
            events.append(dialogue_line)

    full_ass_content = header + "\n".join(events) + "\n"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_ass_content)

    return output_path
