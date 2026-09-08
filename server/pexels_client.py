import os
import requests
from typing import Optional

# Curated fallback clips with diverse cinematic themes that work out-of-the-box
FALLBACK_CLIPS = [
    {
        "id": "mock-nature-1",
        "title": "Mountain Forest Aerial",
        "category": "nature",
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
        "id": "mock-tech-2",
        "title": "Modern City Lights & Technology",
        "category": "tech",
        "duration": 12,
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=640&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
        "preview_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
        "author": "Antigravity Curated",
        "author_url": "https://pexels.com",
        "width": 1920,
        "height": 1080
    },
    {
        "id": "mock-morning-3",
        "title": "Warm Sunrise & Morning Light",
        "category": "morning",
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
        "id": "mock-city-4",
        "title": "Urban Architecture & Skyline",
        "category": "city",
        "duration": 15,
        "image": "https://images.unsplash.com/photo-1477959858617-67f30bc75b82?w=640&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
        "preview_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
        "author": "Antigravity Curated",
        "author_url": "https://pexels.com",
        "width": 1920,
        "height": 1080
    },
    {
        "id": "mock-focus-5",
        "title": "Workspace Deep Focus",
        "category": "focus",
        "duration": 10,
        "image": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=640&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
        "preview_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
        "author": "Antigravity Curated",
        "author_url": "https://pexels.com",
        "width": 1920,
        "height": 1080
    }
]

# Simple query cache to speed up UI interactions
_search_cache = {}

def search_pexels_videos(
    query: str,
    api_key: Optional[str] = None,
    orientation: str = "landscape",
    per_page: int = 12
) -> dict:
    """
    Searches Pexels Video API for stock clips matching the query.
    Falls back to curated stock clips if API key is missing or invalid.
    """
    key = api_key or os.environ.get("PEXELS_API_KEY", "").strip()
    cache_key = f"{query.lower().strip()}_{orientation}_{per_page}_{bool(key)}"
    
    if cache_key in _search_cache:
        return _search_cache[cache_key]

    if not key:
        # Fallback mode
        filtered = [c for c in FALLBACK_CLIPS if any(w in c["title"].lower() or w in c["category"].lower() for w in query.lower().split())]
        results = filtered if filtered else FALLBACK_CLIPS
        response_data = {
            "source": "curated_fallback",
            "message": "Using curated stock footage. Enter a free Pexels API key to unlock millions of live videos.",
            "total_results": len(results),
            "videos": results
        }
        _search_cache[cache_key] = response_data
        return response_data

    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": key,
        "User-Agent": "AudioSyncedVideoMaker/1.0"
    }
    params = {
        "query": query,
        "orientation": orientation if orientation in ["landscape", "portrait"] else "landscape",
        "per_page": min(20, max(4, per_page)),
        "size": "medium"
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        if resp.status_code != 200:
            print(f"Pexels API error ({resp.status_code}): {resp.text}")
            return {
                "source": "curated_fallback",
                "message": f"Pexels API returned status {resp.status_code}. Using curated stock clips.",
                "total_results": len(FALLBACK_CLIPS),
                "videos": FALLBACK_CLIPS
            }

        data = resp.json()
        raw_videos = data.get("videos", [])
        
        parsed_videos = []
        for v in raw_videos:
            v_id = v.get("id")
            duration = v.get("duration", 10)
            image = v.get("image", "")
            user = v.get("user", {})
            author = user.get("name", "Pexels Creator")
            author_url = user.get("url", "https://pexels.com")
            
            # Select best video file
            files = v.get("video_files", [])
            # Priority: hd mp4 (1080p), then largest width mp4, then preview
            mp4_files = [f for f in files if f.get("file_type") == "video/mp4"]
            if not mp4_files:
                continue

            hd_files = [f for f in mp4_files if f.get("quality") == "hd" and f.get("width", 0) >= 1280]
            if hd_files:
                best_file = hd_files[0]
            else:
                # Sort by width
                best_file = max(mp4_files, key=lambda f: f.get("width", 0))

            # Find a lower-resolution preview file if available for fast browser streaming
            preview_files = [f for f in mp4_files if f.get("quality") == "sd" or (f.get("width", 9999) <= 960)]
            preview_url = preview_files[0].get("link") if preview_files else best_file.get("link")

            parsed_videos.append({
                "id": str(v_id),
                "title": f"Pexels Video #{v_id} by {author}",
                "duration": duration,
                "image": image,
                "video_url": best_file.get("link"),
                "preview_url": preview_url,
                "author": author,
                "author_url": author_url,
                "width": best_file.get("width", 1920),
                "height": best_file.get("height", 1080)
            })

        if not parsed_videos:
            # Fallback if query returned no usable video files
            return {
                "source": "curated_fallback",
                "message": f"No video files found for '{query}'. Using curated stock clips.",
                "total_results": len(FALLBACK_CLIPS),
                "videos": FALLBACK_CLIPS
            }

        result_data = {
            "source": "pexels_api",
            "message": f"Found {len(parsed_videos)} live clips from Pexels",
            "total_results": data.get("total_results", len(parsed_videos)),
            "videos": parsed_videos
        }
        _search_cache[cache_key] = result_data
        return result_data

    except Exception as e:
        print(f"Pexels search exception: {e}")
        return {
            "source": "curated_fallback",
            "message": f"Network error connecting to Pexels: {str(e)}. Using curated clips.",
            "total_results": len(FALLBACK_CLIPS),
            "videos": FALLBACK_CLIPS
        }
