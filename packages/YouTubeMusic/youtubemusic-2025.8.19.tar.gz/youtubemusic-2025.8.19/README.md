# YouTubeMusic 🔥
A blazing fast YouTube music search module using DuckDuckGo scraping.

## Features

- No YouTube API needed ✅
- Fast + lightweight async search engine ⚡
- Perfect for Telegram bots, CLI tools, and more 🎧

## Install

```bash
pip install YouTubeMusic

```
# How To Install

```bash
# Search By YouTube Search API
from YouTubeMusic.YtSearch import Search

# Search Using Httpx And Re
from YouTubeMusic.Search import Search
```


# Example Usage
```python

from YouTubeMusic.Search import Search
#from YouTubeMusic.YtSearch import Search

async def SearchYt(query: str):
    results = await Search(query, limit=1)

    if not results or not results.get("main_results"):
        raise Exception("No results found.")

    item = results["main_results"][0] 

    search_data = [{
        "title": item.get("title"),
        "artist": item.get("artist_name"),
        "channel": item.get("channel_name"),
        "duration": item.get("duration"),
        "views": item.get("views"),
        "thumbnail": item.get("thumbnail"),
        "url": item.get("url")
    }]

    song_url = item["url"] 

    return search_data, song_url
```
