import httpx
import os
import random
from .Models import format_dur, process_video

YOUTUBE_API_KEY = [
    "AIzaSyBJ52p5HOl8XTI-i_iKUpk5iPr0LVulp1E",
    "AIzaSyBllgwdS_H8eMeDL6CdifRbbq2F5LYp1mM",
    "AIzaSyC_sd7Hxhhzq_dIuxK5SxKnHr2HlPsUsY0",
    os.getenv("YOUTUBE_API_KEY") ]

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
DETAILS_URL = "https://www.googleapis.com/youtube/v3/videos"

def get_random_key():
    return random.choice([key for key in YOUTUBE_API_KEY if key])
    
async def Search(query: str, limit: int = 1):
    async with httpx.AsyncClient(timeout=10) as client:
        api_key = get_random_key()
 
        search_params = {
            "part": "snippet",
            "q": query,
            "maxResults": limit,
            "type": "video",
            "key": api_key,
        }

        search_res = await client.get(SEARCH_URL, params=search_params)
        if search_res.status_code != 200:
            print("Search error:", search_res.status_code)
            return []

        items = search_res.json().get("items", [])
        video_ids = [item["id"]["videoId"] for item in items]

        if not video_ids:
            return []

        api_key = get_random_key()

        details_params = {
            "part": "contentDetails,statistics",
            "id": ",".join(video_ids),
            "key": api_key,
        }

        detail_res = await client.get(DETAILS_URL, params=details_params)
        detail_items = {v["id"]: v for v in detail_res.json().get("items", [])}

        results = []
        for item in items:
            video_id = item["id"]["videoId"]
            video_details = detail_items.get(video_id)
            if not video_details:
                continue

            video_info = process_video(item, video_details)
            if video_info:
                results.append(video_info)

        return results
