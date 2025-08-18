from setuptools import setup, find_packages

setup(
    name="YouTubeMusic",
    version="2025.08.19",
    description="A YouTube Music Search Package With Artist, Channel, and Video Details",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    author="ABHISHEK THAKUR",
    author_email="abhishekbanshiwal2005@gmail.com",
    url="https://github.com/YouTubeMusicAPI/YouTubeMusic",
    packages=find_packages(),
    install_requires=[
        "httpx[http2]",
        "orjson>=3.9.0",
        "yt-dlp"
    ],
    entry_points={
        'console_scripts': [
            'yt-music=YouTubeMusic.cli:cli',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
