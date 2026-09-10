import re
import math

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves", "also", "just", "like", "get", "make", "really",
    "even", "much", "many", "well", "now", "see", "come", "know", "take"
}

THEME_ASSOCIATIONS = {
    "morning": ["sunrise", "coffee", "morning sunlight", "waking up", "dawn"],
    "night": ["city lights", "stars", "night sky", "neon city", "darkness"],
    "nature": ["forest", "mountains", "river", "trees", "ocean"],
    "mountain": ["mountain peak", "hiking", "clouds", "landscape", "summit"],
    "ocean": ["ocean waves", "beach", "sea", "water surface", "sunset beach"],
    "water": ["clear water", "water drops", "river flow", "ocean", "rain"],
    "work": ["office", "laptop typing", "modern workspace", "business meeting", "coworking"],
    "tech": ["coding screen", "futuristic technology", "cyberpunk", "server room", "smartphone"],
    "technology": ["modern tech", "ai digital", "circuit board", "data connection", "laptop"],
    "business": ["business people", "office skyscraper", "handshake", "corporate meeting", "finance"],
    "success": ["celebration", "winner", "mountain summit", "achievement", "victory"],
    "focus": ["deep work", "reading book", "writing journal", "studying", "headphones"],
    "coffee": ["latte art", "espresso pouring", "cafe atmosphere", "steaming coffee cup"],
    "city": ["city skyline", "urban street", "city timelapse", "skyscrapers", "architecture"],
    "walking": ["person walking", "footsteps street", "forest walk", "travel stroll"],
    "running": ["running athlete", "jogging park", "fitness workout", "track running"],
    "travel": ["airplane flying", "packing luggage", "road trip driving", "scenic view", "passport"],
    "relax": ["yoga meditation", "calm ocean", "peaceful nature", "spa relaxing", "breeze"],
    "growth": ["plant growing", "green seedling", "sunflower blooming", "spring nature"],
    "money": ["cash investment", "stock market graph", "growth finance", "wealth coins"],
    "food": ["cooking kitchen", "delicious meal", "fresh ingredients", "chef cooking", "restaurant"],
    "art": ["painting canvas", "sculpture", "creative drawing", "artistic colors", "palette"],
    "music": ["headphones playing", "guitar strings", "piano keys", "sound equalizer", "dj concert"]
}

def extract_keywords(text: str) -> tuple[str, list[str]]:
    """
    Extracts high-impact visual keywords from a sentence or phrase.
    Returns (primary_search_query, suggested_queries).
    """
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text).lower()
    words = [w for w in cleaned.split() if w and w not in STOP_WORDS and len(w) > 2]

    # Look for thematic matches
    thematic_suggestions = []
    for w in words:
        if w in THEME_ASSOCIATIONS:
            thematic_suggestions.extend(THEME_ASSOCIATIONS[w])

    # Select top distinctive words
    distinctive_words = list(dict.fromkeys(words))[:3]
    
    if distinctive_words:
        primary = " ".join(distinctive_words)
    elif thematic_suggestions:
        primary = thematic_suggestions[0]
    else:
        primary = "cinematic cinematic landscape"

    suggestions = []
    if thematic_suggestions:
        suggestions.extend(thematic_suggestions[:4])
    if len(distinctive_words) >= 2:
        suggestions.append(f"{distinctive_words[0]} cinematic")
        suggestions.append(f"{distinctive_words[-1]} 4k")
    
    if not suggestions:
        suggestions = ["cinematic ambient", "nature beauty", "modern lifestyle", "city lights"]

    # Deduplicate suggestions while keeping order
    final_suggestions = []
    for s in suggestions:
        if s.lower() != primary.lower() and s not in final_suggestions:
            final_suggestions.append(s)

    return primary, final_suggestions[:4]

def segment_script_and_allocate_time(
    script_text: str,
    total_duration: float,
    min_segment_duration: float = 2.5,
    max_segment_duration: float = 8.0
) -> list[dict]:
    """
    Segments a script into coherent scene chunks and allocates time matching total_duration.
    """
    total_duration = max(2.0, float(total_duration))
    
    # 1. Clean script
    text = script_text.strip()
    if not text:
        text = "A cinematic journey through visual landscapes and inspiring moments."

    # 2. Initial sentence splitting
    raw_sentences = [s.strip() for s in re.split(r"(?<=[.!?;\n])\s+", text) if s.strip()]
    if not raw_sentences:
        raw_sentences = [text]

    # 3. Refine segments: if a segment is too long or has too many words, break on clauses
    refined_segments = []
    for sent in raw_sentences:
        words = sent.split()
        if len(words) > 16:
            # Sub-split on commas, dashes or conjunctions
            sub_clauses = [c.strip() for c in re.split(r"[,—–]|\b(?:and|but|while|so)\b", sent) if len(c.strip().split()) >= 3]
            if len(sub_clauses) > 1:
                refined_segments.extend(sub_clauses)
            else:
                refined_segments.append(sent)
        else:
            refined_segments.append(sent)

    # 4. Target number of segments based on total audio duration (aim for 3.5 - 5.0s per clip)
    ideal_scene_count = max(2 if total_duration >= 6.0 else 1, round(total_duration / 4.2))
    
    # If we have too few segments for the audio duration, break text further
    if len(refined_segments) < ideal_scene_count and total_duration >= 6.0:
        further_split = []
        for seg in refined_segments:
            words = seg.split()
            if len(words) >= 6 and len(further_split) + len(refined_segments) <= ideal_scene_count + 1:
                clauses = [c.strip() for c in re.split(r"[,—–;]|\b(?:and|but|while|so|then|as|with)\b", seg) if len(c.strip().split()) >= 2]
                if len(clauses) >= 2:
                    further_split.extend(clauses)
                else:
                    mid = len(words) // 2
                    further_split.append(" ".join(words[:mid]))
                    further_split.append(" ".join(words[mid:]))
            else:
                further_split.append(seg)
        refined_segments = further_split

    # If we have too many short segments for a short audio, merge consecutive short ones
    while len(refined_segments) > 1 and (total_duration / len(refined_segments)) < min_segment_duration:
        # Merge shortest adjacent pair
        shortest_idx = 0
        min_words = 9999
        for i in range(len(refined_segments) - 1):
            combined_len = len(refined_segments[i].split()) + len(refined_segments[i+1].split())
            if combined_len < min_words:
                min_words = combined_len
                shortest_idx = i
        merged = f"{refined_segments[shortest_idx]} {refined_segments[shortest_idx + 1]}"
        refined_segments = (
            refined_segments[:shortest_idx]
            + [merged]
            + refined_segments[shortest_idx + 2:]
        )

    # 5. Calculate word weights for timing distribution
    weights = [max(1, len(s.split())) for s in refined_segments]
    total_words = sum(weights)

    # Raw durations
    raw_durations = [(w / total_words) * total_duration for w in weights]

    # Clamp each duration to reasonably comfortable ranges and re-normalize
    clamped = [max(2.5, min(14.0, d)) for d in raw_durations]
    scale = total_duration / sum(clamped)
    adjusted_durations = [round(d * scale, 2) for d in clamped]

    # Fix rounding residual so sum is exact
    diff = round(total_duration - sum(adjusted_durations), 2)
    if adjusted_durations:
        adjusted_durations[-1] = round(adjusted_durations[-1] + diff, 2)

    # 6. Build final scene objects with timestamps and keywords
    scenes = []
    current_time = 0.0
    for idx, (seg_text, dur) in enumerate(zip(refined_segments, adjusted_durations)):
        start = round(current_time, 2)
        end = round(current_time + dur, 2)
        current_time = end

        primary_q, suggestions = extract_keywords(seg_text)

        scenes.append({
            "id": idx + 1,
            "text": seg_text,
            "start_time": start,
            "end_time": end,
            "duration": dur,
            "formatted_time": f"{int(start//60):02d}:{start%60:04.1f} - {int(end//60):02d}:{end%60:04.1f}",
            "primary_query": primary_q,
            "suggested_queries": suggestions,
            "selected_clip": None
        })

    return scenes
