import pkg_resources
import httpx
import asyncio

async def check_for_update(package_name: str = "YouTubeMusic"):
    try:
        current_version = pkg_resources.get_distribution(package_name).version
        url = f"https://pypi.org/pypi/{package_name}/json"
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            latest_version = resp.json()['info']['version']
        if current_version != latest_version:
            print(f"⚠️ New version available for {package_name}!")
            print(f"Current version: {current_version}")
            print(f"Latest version: {latest_version}")
            print(f"Run: pip install --upgrade {package_name} to update.")
    except Exception:
        pass

if __name__ == "__main__":
    asyncio.run(check_for_update())
  
