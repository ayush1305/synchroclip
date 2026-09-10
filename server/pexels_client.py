import os
import requests
from typing import Optional

# Attempt to load .env file if it exists
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

FALLBACK_CLIPS = [
    {
        "id": "clip-tech-code",
        "title": "Modern Coding & Cyber Technology",
        "category": "Technology",
        "tags": ["tech", "coding", "code", "programming", "developer", "computer", "future", "ai", "digital"],
        "duration": 15,
        "image": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=640&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
        "preview_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
        "author": "Antigravity Curated",
        "author_url": "https://pexels.com",
        "width": 1920,
        "height": 1080
    },
    {
        "id": "clip-nature-mountain",
        "title": "Mountain Forest Aerial View",
        "category": "Nature",
        "tags": ["nature", "mountain", "forest", "trees", "landscape", "adventure", "earth", "scenic"],
        "duration": 15,
        "image": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=640&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        "preview_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        "author": "Antigravity Curated",
        "author_url": "https://pexels.com",
        "width": 1920,
        "height": 1080
    },
    {
        "id": "clip-city-night",
        "title": "Neon Metropolis & City Traffic",
        "category": "City",
        "tags": ["city", "traffic", "night", "neon", "lights", "skyline", "urban", "street", "metropolis"],
        "duration": 15,
        "image": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=640&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
        "preview_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
        "author": "Antigravity Curated",
        "author_url": "https://pexels.com",
        "width": 1920,
        "height": 1080
    },
    {
        "id": "clip-sunrise-morning",
        "title": "Golden Sunrise & Morning Horizon",
        "category": "Nature",
        "tags": ["morning", "sunrise", "sun", "dawn", "light", "hope", "begin", "start", "horizon", "sunlight"],
        "duration": 14,
        "image": "https://images.unsplash.com/photo-1470240731273-7821a6eeb6bd?w=640&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyBlazes.mp4",
        "preview_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyBlazes.mp4",
        "author": "Antigravity Curated",
        "author_url": "https://pexels.com",
        "width": 1920,
        "height": 1080
    },
    {
        "id": "clip-focus-workspace",
        "title": "Deep Work & Creative Studio",
        "category": "Business",
        "tags": ["focus", "work", "office", "study", "laptop", "creative", "desk", "productive", "business"],
        "duration": 12,
        "image": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=640&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
        "preview_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
        "author": "Antigravity Curated",
        "author_url": "https://pexels.com",
        "width": 1920,
        "height": 1080
    },
    {
        "id": "clip-ocean-waves",
        "title": "Cinematic Turquoise Ocean Waves",
        "category": "Nature",
        "tags": ["ocean", "waves", "water", "sea", "beach", "calm", "relax", "blue", "surf", "coastal"],
        "duration": 15,
        "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=640&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
        "preview_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
        "author": "Antigravity Curated",
        "author_url": "https://pexels.com",
        "width": 1920,
        "height": 1080
    },
    {
        "id": "clip-energy-motion",
        "title": "High Energy Speed & Kinetic Motion",
        "category": "Fitness",
        "tags": ["energy", "speed", "fast", "motion", "action", "dynamic", "power", "racing", "workout"],
        "duration": 15,
        "image": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=640&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
        "preview_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
        "author": "Antigravity Curated",
        "author_url": "https://pexels.com",
        "width": 1920,
        "height": 1080
    },
    {
        "id": "clip-cosmic-galaxy",
        "title": "Cosmic Stars & Deep Nebula",
        "category": "Space",
        "tags": ["space", "stars", "galaxy", "universe", "cosmic", "mystery", "infinite", "night", "dark"],
        "duration": 15,
        "image": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=640&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackSeeTheWorld.mp4",
        "preview_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackSeeTheWorld.mp4",
        "author": "Antigravity Curated",
        "author_url": "https://pexels.com",
        "width": 1920,
        "height": 1080
    },
    {
        "id": "clip-fitness-athlete",
        "title": "Athletic Training & Determination",
        "category": "Fitness",
        "tags": ["fitness", "gym", "athlete", "workout", "strength", "running", "focus", "training", "power"],
        "duration": 14,
        "image": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=640&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
        "preview_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
        "author": "Antigravity Curated",
        "author_url": "https://pexels.com",
        "width": 1920,
        "height": 1080
    },
    {
        "id": "clip-abstract-light",
        "title": "Abstract Prism & Light Flow",
        "category": "Abstract",
        "tags": ["abstract", "prism", "light", "colors", "glow", "creative", "art", "design", "vibe"],
        "duration": 12,
        "image": "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=640&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "preview_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "author": "Antigravity Curated",
        "author_url": "https://pexels.com",
        "width": 1920,
        "height": 1080
    }
]

_search_cache = {}

def get_pexels_api_key(passed_key: Optional[str] = None) -> str:
    if passed_key and passed_key.strip():
        return passed_key.strip()
    return os.environ.get("PEXELS_API_KEY", "").strip()

def search_pexels_videos(
    query: str,
    api_key: Optional[str] = None,
    orientation: str = "landscape",
    per_page: int = 15,
    page: int = 1
) -> dict:
    key = get_pexels_api_key(api_key)
    query_clean = (query or "").strip()
    cache_key = f"{query_clean.lower()}_{orientation}_{per_page}_{page}_{bool(key)}"

    if cache_key in _search_cache:
        return _search_cache[cache_key]

    if not key or key == "your_pexels_api_key_here":
        query_words = set(query_clean.lower().split()) if query_clean else set()
        scored = []
        for c in FALLBACK_CLIPS:
            score = 0
            all_words = set(c["tags"] + [c["category"].lower()] + c["title"].lower().split())
            if query_words & all_words:
                score += len(query_words & all_words) * 3
            elif not query_words:
                score = 1
            scored.append((score, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [x[1] for x in scored if x[0] > 0]
        if not results:
            results = FALLBACK_CLIPS

        response_data = {
            "source": "curated_stock",
            "message": "Showing curated high-definition stock videos. Add PEXELS_API_KEY in .env for live Pexels search.",
            "total_results": len(results),
            "page": page,
            "per_page": per_page,
            "videos": results[:per_page]
        }
        _search_cache[cache_key] = response_data
        return response_data

    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": key,
        "User-Agent": "SynchroClipVideoEditor/2.0"
    }
    params = {
        "query": query_clean or "cinematic scenery",
        "orientation": orientation if orientation in ["landscape", "portrait", "square"] else "landscape",
        "per_page": min(30, max(4, per_page)),
        "page": max(1, page),
        "size": "medium"
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=8)
        if resp.status_code != 200:
            return search_pexels_videos(query=query, api_key=None, orientation=orientation, per_page=per_page, page=page)

        data = resp.json()
        raw_videos = data.get("videos", [])
        parsed_videos = []
        for v in raw_videos:
            v_id = v.get("id")
            files = v.get("video_files", [])
            mp4_files = [f for f in files if f.get("file_type") == "video/mp4"]
            if not mp4_files:
                continue

            hd_files = [f for f in mp4_files if f.get("quality") == "hd" and f.get("width", 0) >= 1280]
            best_file = hd_files[0] if hd_files else max(mp4_files, key=lambda f: f.get("width", 0))
            preview_files = [f for f in mp4_files if f.get("quality") == "sd" or (f.get("width", 9999) <= 960)]
            preview_url = preview_files[0].get("link") if preview_files else best_file.get("link")

            parsed_videos.append({
                "id": str(v_id),
                "title": f"Pexels #{v_id}",
                "category": "Stock",
                "duration": v.get("duration", 10),
                "image": v.get("image", ""),
                "video_url": best_file.get("link"),
                "preview_url": preview_url,
                "author": v.get("user", {}).get("name", "Pexels Creator"),
                "author_url": v.get("user", {}).get("url", "https://pexels.com"),
                "width": best_file.get("width", 1920),
                "height": best_file.get("height", 1080)
            })

        if not parsed_videos:
            return search_pexels_videos(query=query, api_key=None, orientation=orientation, per_page=per_page, page=page)

        res = {
            "source": "pexels_api",
            "total_results": data.get("total_results", len(parsed_videos)),
            "page": page,
            "per_page": per_page,
            "videos": parsed_videos
        }
        _search_cache[cache_key] = res
        return res
    except Exception as e:
        print(f"Pexels fetch failed: {e}")
        return search_pexels_videos(query=query, api_key=None, orientation=orientation, per_page=per_page, page=page)

def select_distinct_clip(query: str, scene_idx: int, used_clip_ids: set, api_key: Optional[str] = None) -> dict:
    res = search_pexels_videos(query=query, api_key=api_key)
    videos = res.get("videos", [])
    for v in videos:
        if v["id"] not in used_clip_ids:
            used_clip_ids.add(v["id"])
            return v
    for c in FALLBACK_CLIPS:
        if c["id"] not in used_clip_ids:
            used_clip_ids.add(c["id"])
            return c
    idx = scene_idx % len(FALLBACK_CLIPS)
    return FALLBACK_CLIPS[idx]
