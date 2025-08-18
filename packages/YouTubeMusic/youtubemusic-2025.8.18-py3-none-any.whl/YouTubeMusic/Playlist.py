import httpx
import re
import json
import asyncio

async def fetch_playlist_page(playlist_id: str) -> str:
    url = f"https://www.youtube.com/playlist?list={playlist_id}" 
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text


def extract_yt_initial_data(html: str) -> dict:
    patterns = [
        r"var ytInitialData = ({.*?});</script>",
        r'window\["ytInitialData"\] = ({.*?});',
        r"window\.ytInitialData = ({.*?});"
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.DOTALL)
        if match:
            json_str = match.group(1)
            return json.loads(json_str)
    raise ValueError("ytInitialData not found in page")

def parse_playlist_songs(data: dict) -> list:
    songs = []
    try:
        videos = data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]\
            ["content"]["sectionListRenderer"]["contents"][0]["playlistVideoListRenderer"]["contents"]

        for video in videos:
            video_data = video.get("playlistVideoRenderer")
            if not video_data:
                continue

            song = {
                "videoId": video_data["videoId"],
                "title": video_data["title"]["simpleText"],
                "channel": video_data.get("shortBylineText", {}).get("runs", [{}])[0].get("text", ""),
                "duration": video_data.get("lengthSeconds", "N/A"),
                "url": f"https://music.youtube.com/watch?v={video_data['videoId']}"
            }
            songs.append(song)

    except Exception:
        pass
    return songs

async def get_playlist_songs(playlist_id: str) -> list:
    html = await fetch_playlist_page(playlist_id)
    data = extract_yt_initial_data(html)
    print(json.dumps(data, indent=2))  # Debug
    songs = parse_playlist_songs(data)
    return songs
