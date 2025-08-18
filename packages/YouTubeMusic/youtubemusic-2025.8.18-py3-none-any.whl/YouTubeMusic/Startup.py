import requests
from colorama import init, Fore, Style
from YouTubeMusic import __version__, __author__

init(autoreset=True)

def check_latest_version(pkg_name="YouTubeMusic"):
    try:
        response = requests.get(f"https://pypi.org/pypi/{pkg_name}/json", timeout=3)
        if response.status_code == 200:
            return response.json()["info"]["version"]
    except Exception:
        return None

def print_startup_message():
    print(Fore.GREEN + "✅  YouTubeMusic started...\n")

    print(Fore.CYAN + f"Version : {__version__}")
    print(Fore.CYAN + f"Author  : {__author__}")
    print(Fore.CYAN + "License : MIT")
    print(Fore.CYAN + "GitHub  : https://github.com/YouTubeMusicAPI/YouTubeMusic")

    latest = check_latest_version("YouTubeMusic")
    if latest and latest != __version__:
        print(Fore.YELLOW + "\nUpdate Available!")
        print(Fore.YELLOW + f"New YouTubeMusic v{latest} is now available!")
    else:
        print(Fore.GREEN + "\nYou are using the latest version!")
