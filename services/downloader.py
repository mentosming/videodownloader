import yt_dlp
import asyncio
import os

class YTDownloader:
    def __init__(self):
        # We can configure options here. 
        # Note: quiet=True to avoid spamming the console
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False, # We want full formats, not just list
            'skip_download': True, # We only extract info!
        }
        
        # Check if cookies.txt exists in the root directory
        # This is essential for bypassing YouTube bot detection on cloud servers
        if os.path.exists("cookies.txt"):
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
