from urllib.parse import quote_plus
import httpx
import re
import orjson
from .Utils import format_views

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

YOUTUBE_SEARCH_URL = "https://www.youtube.com/results?search_query={}"

_cache = {}

yt_data_regex = re.compile(r"ytInitialData\s*=\s*(\{.+?\});", re.DOTALL)


_client = httpx.AsyncClient(http2=True, timeout=5.0, limits=httpx.Limits(max_connections=10, max_keepalive_connections=5))

async def Search(query: str, limit: int = 1, client=None):
    if query in _cache:
        return _cache[query]

    search_url = YOUTUBE_SEARCH_URL.format(quote_plus(query))
    if client is None:
        client = _client

    try:
        response = await client.get(search_url, headers=HEADERS)
    except Exception as e:
        print(f"[!] Request failed: {e}")
        return {"main_results": [], "suggested": []}

    match = yt_data_regex.search(response.text)
    if not match:
        return {"main_results": [], "suggested": []}

    try:
        data = orjson.loads(match.group(1))
        results = []

        sections = data.get("contents", {}) \
            .get("twoColumnSearchResultsRenderer", {}) \
            .get("primaryContents", {}) \
            .get("sectionListRenderer", {}) \
            .get("contents", [])

        for section in sections:
            items = section.get("itemSectionRenderer", {}).get("contents", [])
            for item in items:
                if "videoRenderer" in item:
                    v = item["videoRenderer"]
                    results.append({
                        "type": "video",
                        "title": v["title"]["runs"][0]["text"],
                        "url": f"https://www.youtube.com/watch?v={v['videoId']}",
                        "duration": v.get("lengthText", {}).get("simpleText", "LIVE"),
                        "channel_name": v.get("ownerText", {}).get("runs", [{}])[0].get("text", "Unknown"),
                        "views": format_views(v.get("viewCountText", {}).get("simpleText", "0 views")),
                        "thumbnail": v["thumbnail"]["thumbnails"][-1]["url"],
                    })

                if len(results) >= limit:
                    break
            if len(results) >= limit:
                break

        output = {
            "main_results": results[:limit],
            "suggested": results[limit:limit + 5],
        }

        _cache[query] = output
        return output

    except Exception as e:
        print(f"[!] Parse error: {e}")
        return {"main_results": [], "suggested": []}
