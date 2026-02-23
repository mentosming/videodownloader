import yt_dlp
import asyncio
import os
import tempfile
import shutil
from typing import Any

class YTDownloader:
    def __init__(self):
        # We can configure options here. 
        # Note: quiet=True to avoid spamming the console
        self.ydl_opts: dict[str, Any] = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False, # We want full formats, not just list
            'skip_download': True, # We only extract info!
        }
        
        # Check if cookies.txt exists in the root directory
        # This is essential for bypassing YouTube bot detection on cloud servers
        if os.path.exists("cookies.txt"):
            try:
                # Copy to temp directory to avoid read-only file system errors on cloud/serverless environments
                temp_cookie_path = os.path.join(tempfile.gettempdir(), "yt_cookies.txt")
                shutil.copy2("cookies.txt", temp_cookie_path)
                self.ydl_opts['cookiefile'] = temp_cookie_path
            except Exception as e:
                # Fallback to local file if copying fails
                print(f"Failed to copy cookies to temp dir: {e}")
                self.ydl_opts['cookiefile'] = "cookies.txt"



    async def extract_info(self, url: str) -> dict:
        """
        Extract video information asynchronously.
        Run yt-dlp in a thread pool to avoid blocking the async event loop.
        """
        def _extract():
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)

        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, _extract)
        return info
