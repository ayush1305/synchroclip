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

def hex_to_ass_color(hex_str: str) -> str:
    """
    Converts RGB hex color string (e.g. #FF0055) to ASS BGR format &H00BBGGRR&
    """
    cleaned = hex_str.strip().lstrip("#")
    if len(cleaned) == 6 and all(c in "0123456789abcdefABCDEF" for c in cleaned):
        r = cleaned[0:2]
        g = cleaned[2:4]
        b = cleaned[4:6]
        return f"&H00{b}{g}{r}&".upper()
    elif len(cleaned) == 3 and all(c in "0123456789abcdefABCDEF" for c in cleaned):
        r = cleaned[0] * 2
        g = cleaned[1] * 2
        b = cleaned[2] * 2
        return f"&H00{b}{g}{r}&".upper()
    return "&H0000FFFF&"

def generate_ass_subtitles(
    caption_cards: list[dict],
    template_id: str = "hormozi_classic",
    highlight_color_key: str = "yellow",
    primary_color_key: Optional[str] = None,
    output_path: str = "captions.ass",
    width: int = 1920,
    height: int = 1080,
    font_family_override: Optional[str] = None,
    hero_font_override: Optional[str] = None,
    enable_shine: bool = False,
    progressive_reveal: bool = False,
    word_zoom: bool = False,
    marker_style: str = "none",
    marker_color: str = "#4ade80"
) -> str:
    """
    Generates Advanced SubStation Alpha (.ass) subtitle file with word-by-word
    karaoke highlighting, dual-color styling, multi-font graphic rendering,
    progressive word reveals, word zoom, and marker decorations.
    """
    has_any_template = (template_id != "none") or any(
        (c.get("template_id") or c.get("template")) not in (None, "", "none") for c in caption_cards
    )
    if not has_any_template:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("")
        return output_path

    # Collect all template IDs used across cards
    used_template_ids = []
    if template_id != "none":
        used_template_ids.append(template_id)
    for c in caption_cards:
        ctid = c.get("template_id") or c.get("template")
        if ctid and ctid != "none" and ctid not in used_template_ids:
            used_template_ids.append(ctid)

    default_for_header = template_id if template_id != "none" else (used_template_ids[0] if used_template_ids else "hormozi_classic")
    header = caption_templates.build_multi_ass_header(
        template_ids=used_template_ids,
        default_template_id=default_for_header,
        width=width,
        height=height,
        font_override=font_family_override
    )

    # Global fallback highlight color (Color 2 - Active / Hero Word)
    cleaned_high = highlight_color_key.strip().lstrip("#") if highlight_color_key else ""
    if len(cleaned_high) in (3, 6) and all(c in "0123456789abcdefABCDEF" for c in cleaned_high):
        global_highlight_ass = hex_to_ass_color(highlight_color_key)
    elif highlight_color_key in caption_templates.HIGHLIGHT_COLORS:
        color_info = caption_templates.HIGHLIGHT_COLORS[highlight_color_key]
        global_highlight_ass = color_info["ass"] if color_info["ass"].endswith("&") else f"{color_info['ass']}&"
    else:
        global_highlight_ass = "&H0000FFFF&"

    # Global fallback primary color (Color 1 - Base Words)
    default_tpl = caption_templates.get_template(default_for_header)
    if primary_color_key:
        cleaned_prim = primary_color_key.strip().lstrip("#")
        if len(cleaned_prim) in (3, 6) and all(c in "0123456789abcdefABCDEF" for c in cleaned_prim):
            global_primary_ass = hex_to_ass_color(primary_color_key)
        elif primary_color_key in caption_templates.HIGHLIGHT_COLORS:
            color_info = caption_templates.HIGHLIGHT_COLORS[primary_color_key]
            global_primary_ass = color_info["ass"] if color_info["ass"].endswith("&") else f"{color_info['ass']}&"
        else:
            global_primary_ass = default_tpl.get("primary_color", "&H00FFFFFF&")
    else:
        global_primary_ass = default_tpl.get("primary_color", "&H00FFFFFF&")

    if not global_primary_ass.endswith("&"):
        global_primary_ass = f"{global_primary_ass}&"

    events = []

    for card in caption_cards:
        words = card.get("words", [])
        if not words:
            continue

        card_tpl_id = card.get("template_id") or card.get("template") or template_id
        if card_tpl_id == "none":
            # Explicitly hidden for this card
            continue

        card_tpl = caption_templates.get_template(card_tpl_id)
        style_name = f"Style_{card_tpl_id}" if card_tpl_id != default_for_header and card_tpl_id in used_template_ids else "Default"

        # Determine fonts for this card
        card_body_font = card.get("font_family") or font_family_override or card_tpl.get("body_font") or card_tpl.get("fontname") or "Montserrat"
        card_hero_font = card.get("hero_font") or hero_font_override or card_tpl.get("hero_font") or card_body_font
        card_hero_italic = card_tpl.get("hero_italic", 0)
        card_hero_scale = card_tpl.get("hero_scale", 118)
        card_is_multi_font = card_tpl.get("is_multi_font", False) or bool(card_hero_font != card_body_font)

        # Word zoom override for this card
        card_word_zoom = card.get("word_zoom") if card.get("word_zoom") is not None else word_zoom
        if card_word_zoom:
            card_hero_scale = max(140, card_hero_scale + 20)

        # Progressive reveal override for this card
        card_progressive = card.get("progressive_reveal") if card.get("progressive_reveal") is not None else progressive_reveal

        # Marker style for this card
        card_marker = card.get("marker_style") if card.get("marker_style") and card.get("marker_style") != "none" else (
            marker_style if marker_style != "none" else card_tpl.get("marker_style", "none")
        )
        card_marker_color = card.get("marker_color") or marker_color or card_tpl.get("marker_color", "#4ade80")
        card_marker_ass = hex_to_ass_color(card_marker_color)

        # Highlight color for this card
        if card.get("highlight_color"):
            c_high = card["highlight_color"].strip().lstrip("#")
            if len(c_high) in (3, 6) and all(c in "0123456789abcdefABCDEF" for c in c_high):
                card_highlight_ass = hex_to_ass_color(card["highlight_color"])
            elif card["highlight_color"] in caption_templates.HIGHLIGHT_COLORS:
                card_highlight_ass = caption_templates.HIGHLIGHT_COLORS[card["highlight_color"]]["ass"]
            else:
                card_highlight_ass = global_highlight_ass
        elif card.get("template_id") and card["template_id"] != template_id:
            card_highlight_ass = card_tpl.get("secondary_color", global_highlight_ass)
        else:
            card_highlight_ass = global_highlight_ass
        if not card_highlight_ass.endswith("&"):
            card_highlight_ass = f"{card_highlight_ass}&"

        # Primary color for this card
        if card.get("primary_color"):
            c_prim = card["primary_color"].strip().lstrip("#")
            if len(c_prim) in (3, 6) and all(c in "0123456789abcdefABCDEF" for c in c_prim):
                card_primary_ass = hex_to_ass_color(card["primary_color"])
            elif card["primary_color"] in caption_templates.HIGHLIGHT_COLORS:
                card_primary_ass = caption_templates.HIGHLIGHT_COLORS[card["primary_color"]]["ass"]
            else:
                card_primary_ass = global_primary_ass
        elif card.get("template_id") and card["template_id"] != template_id:
            card_primary_ass = card_tpl.get("primary_color", global_primary_ass)
        else:
            card_primary_ass = global_primary_ass
        if not card_primary_ass.endswith("&"):
            card_primary_ass = f"{card_primary_ass}&"

        card_anim = card.get("animation") or card_tpl.get("animation", "bounce")
        is_hierarchy = (card_tpl.get("category") == "Viral Hierarchy") or card_tpl.get("is_hierarchy", False)

        for target_idx, active_word in enumerate(words):
            slice_start = to_ass_time(active_word["start"])
            slice_end = to_ass_time(active_word["end"])

            if is_hierarchy and len(words) >= 2:
                total_w = len(words)
                if total_w >= 5:
                    l1_end = 2
                    l2_end = 4
                elif total_w == 4:
                    l1_end = 1
                    l2_end = 3
                elif total_w == 3:
                    l1_end = 1
                    l2_end = 2
                else:
                    l1_end = 1
                    l2_end = 2

                line1_parts = []
                line2_parts = []
                line3_parts = []

                for idx, w in enumerate(words):
                    if card_progressive and idx > target_idx:
                        continue
                    word_text = w["word"]
                    is_hero = (idx >= l1_end and idx < l2_end)
                    word_font = card_hero_font if is_hero else card_body_font

                    if idx == target_idx:
                        extra_tags = f"\\fn{word_font}"
                        if card_hero_italic and is_hero:
                            extra_tags += "\\i1"
                        marker_tags = ""
                        if card_marker == "underline":
                            marker_tags += "\\u1"
                        elif card_marker == "box":
                            marker_tags += f"\\bord5\\3c{card_marker_ass}"
                        elif card_marker == "circle":
                            marker_tags += f"\\bord4\\3c{card_marker_ass}"

                        shine_tag = "\\bord4\\blur3" if enable_shine else ""
                        active_scale = card_hero_scale if is_hero else int(card_hero_scale * 0.9)
                        zoom_fx = f"\\t(0,140,\\fscx{active_scale-12}\\fscy{active_scale-12})" if card_word_zoom else ""
                        rendered_word = f"{{\\c{card_highlight_ass}{extra_tags}{marker_tags}{shine_tag}\\fscx{active_scale}\\fscy{active_scale}{zoom_fx}}}{word_text}{{\\r}}"
                    else:
                        base_c = card_highlight_ass if is_hero else card_primary_ass
                        extra_f = f"\\fn{word_font}" if is_hero else f"\\fn{card_body_font}"
                        rendered_word = f"{{{extra_f}\\c{base_c}}}{word_text}"

                    if idx < l1_end:
                        line1_parts.append(rendered_word)
                    elif idx < l2_end:
                        line2_parts.append(rendered_word)
                    else:
                        line3_parts.append(rendered_word)

                valid_lines = []
                if line1_parts:
                    valid_lines.append(f"{{\\fs46}}" + " ".join(line1_parts))
                if line2_parts:
                    valid_lines.append(f"{{\\fs82\\b1}}" + " ".join(line2_parts))
                if line3_parts:
                    valid_lines.append(f"{{\\fs48}}" + " ".join(line3_parts))

                line_text = "\\N".join(valid_lines)
            else:
                line_parts = []
                for idx, w in enumerate(words):
                    if card_progressive and idx > target_idx:
                        continue

                    word_text = w["word"]
                    if idx == target_idx:
                        extra_tags = ""
                        if card_is_multi_font and card_hero_font != card_body_font:
                            extra_tags += f"\\fn{card_hero_font}"
                        if card_hero_italic:
                            extra_tags += "\\i1"

                        # Marker decoration tags
                        marker_tags = ""
                        if card_marker == "underline":
                            marker_tags += "\\u1"
                        elif card_marker == "box":
                            marker_tags += f"\\bord5\\3c{card_marker_ass}"
                        elif card_marker == "circle":
                            marker_tags += f"\\bord4\\3c{card_marker_ass}"

                        shine_tag = "\\bord4\\blur3" if enable_shine else ""
                        zoom_fx = f"\\t(0,140,\\fscx{card_hero_scale-12}\\fscy{card_hero_scale-12})" if card_word_zoom else ""

                        if card_anim in ("bounce", "spring", "elastic", "jelly"):
                            line_parts.append(f"{{\\c{card_highlight_ass}{extra_tags}{marker_tags}{shine_tag}\\fscx{card_hero_scale}\\fscy{card_hero_scale}{zoom_fx}}}{word_text}{{\\r}}")
                        elif card_anim in ("word_zoom", "mega_zoom", "stomp", "zoom"):
                            line_parts.append(f"{{\\c{card_highlight_ass}{extra_tags}{marker_tags}{shine_tag}\\fscx{max(128, card_hero_scale)}\\fscy{max(128, card_hero_scale)}{zoom_fx}}}{word_text}{{\\r}}")
                        elif card_anim in ("glow_pulse", "neon_glow", "aura", "laser", "glow"):
                            if enable_shine:
                                line_parts.append(f"{{\\c{card_highlight_ass}{extra_tags}{marker_tags}\\bord5\\blur4\\fscx{card_hero_scale}\\fscy{card_hero_scale}{zoom_fx}}}{word_text}{{\\r}}")
                            else:
                                line_parts.append(f"{{\\c{card_highlight_ass}{extra_tags}{marker_tags}\\fscx{card_hero_scale}\\fscy{card_hero_scale}{zoom_fx}}}{word_text}{{\\r}}")
                        elif card_anim in ("fire_pulse", "firestorm"):
                            if enable_shine:
                                line_parts.append(f"{{\\c{card_highlight_ass}{extra_tags}{marker_tags}\\bord6\\3c&H000000FF&\\fscx{card_hero_scale}\\fscy{card_hero_scale}{zoom_fx}}}{word_text}{{\\r}}")
                            else:
                                line_parts.append(f"{{\\c{card_highlight_ass}{extra_tags}{marker_tags}\\fscx{card_hero_scale}\\fscy{card_hero_scale}{zoom_fx}}}{word_text}{{\\r}}")
                        elif card_anim in ("comic_pop", "boom", "pop"):
                            line_parts.append(f"{{\\c{card_highlight_ass}{extra_tags}{marker_tags}{shine_tag}\\fscx{max(126, card_hero_scale)}\\fscy{max(126, card_hero_scale)}{zoom_fx}}}{word_text}{{\\r}}")
                        elif card_anim in ("slide_up", "drift_left", "diagonal", "elevator", "wave", "slide"):
                            line_parts.append(f"{{\\c{card_highlight_ass}{extra_tags}{marker_tags}{shine_tag}\\fscx{card_hero_scale}\\fscy{card_hero_scale}{zoom_fx}}}{word_text}{{\\r}}")
                        elif card_anim in ("glitch", "pixel", "retro_vhs", "matrix"):
                            line_parts.append(f"{{\\c{card_highlight_ass}{extra_tags}{marker_tags}{shine_tag}\\fscx{card_hero_scale}\\fscy{card_hero_scale}{zoom_fx}}}{word_text}{{\\r}}")
                        else:
                            line_parts.append(f"{{\\c{card_highlight_ass}{extra_tags}{marker_tags}{shine_tag}\\fscx{card_hero_scale}\\fscy{card_hero_scale}{zoom_fx}}}{word_text}{{\\r}}")
                    else:
                        if card_is_multi_font and card_hero_font != card_body_font:
                            line_parts.append(f"{{\\fn{card_body_font}\\c{card_primary_ass}}}{word_text}")
                        else:
                            line_parts.append(f"{{\\c{card_primary_ass}}}{word_text}")

                line_text = " ".join(line_parts)
            dialogue_line = f"Dialogue: 0,{slice_start},{slice_end},{style_name},,0,0,0,,{line_text}"
            events.append(dialogue_line)

    full_ass_content = header + "\n".join(events) + "\n"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_ass_content)

    return output_path
