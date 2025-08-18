import asyncio
import argparse
from YouTubeMusic.Search import Search
from YouTubeMusic.Update import check_for_update
from YouTubeMusic.Stream import get_audio_url
from YouTubeMusic import __version__, __author__


async def run_search(query: str, fetch_audio: bool = False):
    update_msg = await check_for_update()
    if update_msg:
        print(update_msg)

    results = await Search(query, limit=1)

    if not results or not results.get("main_results"):
        print("❌ No results found.")
        return

    item = results["main_results"][0]
    print("\n🎵 Result")
    print("Type      :", item.get("type", "video"))
    print("Title     :", item["title"])
    print("Channel   :", item["channel_name"])
    print("Views     :", item["views"])
    print("Duration  :", item["duration"])
    print("Thumbnail :", item["thumbnail"])
    print("URL       :", item["url"])

    if fetch_audio:
        print("\n🔊 Extracting audio stream URL...")
        audio_url = get_audio_url(item["url"])
        if audio_url:
            print("✅ Audio URL:", audio_url)
        else:
            print("❌ Failed to extract audio URL.")


def cli():
    parser = argparse.ArgumentParser(prog="YouTubeMusic")
    parser.add_argument('query', nargs='*', help='Song name or YouTube URL')
    parser.add_argument('--stream', action='store_true', help='Also extract audio stream URL')
    parser.add_argument('--version', action='version', version=f'YouTubeMusic {__version__}')
    parser.add_argument('--info', action='store_true', help='Show version, author & contact info')

    args = parser.parse_args()

    if args.info:
        print(f"YouTubeMusic Version: {__version__}")
        print(f"Author: {__author__}")
        print("Contacts: Telegram - @AboutRealAbhi")
        return

    if not args.query:
        print("Please provide a search query.")
        return

    query = " ".join(args.query)
    asyncio.run(run_search(query, fetch_audio=args.stream))


if __name__ == "__main__":
    cli()
