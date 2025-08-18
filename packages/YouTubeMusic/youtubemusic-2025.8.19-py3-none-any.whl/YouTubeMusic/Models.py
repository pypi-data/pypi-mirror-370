from .Utils import parse_dur, format_ind


def format(n):
    return format_ind(n)
    
def format_dur(duration_str):
    return parse_dur(duration_str)

def process_video(item, details):
    try:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        channel = item["snippet"]["channelTitle"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        thumbnail = item["snippet"]["thumbnails"]["high"]["url"]

        duration = details.get("contentDetails", {}).get("duration", "N/A")
        views = details.get("statistics", {}).get("viewCount", "N/A")

        artist = extract_artist(title) or channel

        return {
            "title": title,
            "url": url,
            "artist_name": artist,
            "channel_name": channel,
            "views": format(views),
            "duration": format_dur(duration),
            "thumbnail": thumbnail,
        }
    except Exception as e:
        print("Error processing video item:", e)
        return None



def extract_artist(title: str):
    artist_name = title.split("-")[0].strip() if "-" in title else None
    return artist_name or "Unknown Artist"
