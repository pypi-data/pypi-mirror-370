import re
import urllib.parse as urlparse

def extract_playlist_id(url: str) -> str:
    query = urlparse.urlparse(url).query
    params = urlparse.parse_qs(query)
    if "list" in params:
        return params["list"][0]
    return ""
    
def parse_dur(duration):
    match = re.match(
        r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration
    )
    if not match:
        return "N/A"

    hours, minutes, seconds = match.groups(default="0")
    h, m, s = int(hours), int(minutes), int(seconds)

    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"

def format_ind(n):
    n = int(n)
    if n >= 10**7:
        return f"{n/10**7:.1f} Crore"
    elif n >= 10**5:
        return f"{n/10**5:.1f} Lakh"
    elif n >= 10**3:
        return f"{n/10**3:.1f}K"
    return str(n)
    
def format_views(views_str):
    views_cleaned = ''.join(filter(str.isdigit, views_str.replace(' ', '')))
    if 'M' in views_str:
        return format_ind(float(views_cleaned) * 10**6)
    elif 'K' in views_str:
        return format_ind(float(views_cleaned) * 10**3)
    elif views_cleaned:
        return format_ind(views_cleaned)
    return "N/A"
