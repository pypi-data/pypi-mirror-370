import subprocess
import json

def get_audio_url(video_url: str, cookies_path: str = None) -> str | None:
    try:
        cmd = [
            "yt-dlp",
            "-j",
            "-f", "bestaudio[ext=m4a]/bestaudio",
            "--no-playlist",
            "--no-check-certificate",
        ]

        if cookies_path:
            cmd += ["--cookies", cookies_path]

        cmd.append(video_url)

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print("❌ yt-dlp error:", result.stderr)
            return None

        data = json.loads(result.stdout)
        return data["url"]

    except Exception as e:
        print(f"❌ Error extracting stream URL: {e}")
        return None
