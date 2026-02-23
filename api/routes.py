from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from services.downloader import YTDownloader

router = APIRouter()
downloader = YTDownloader()

class ExtractRequest(BaseModel):
    url: HttpUrl

class VideoFormat(BaseModel):
    format_id: str
    ext: str
    resolution: str
    filesize: Optional[int]
    url: str
    vcodec: str
    acodec: str

class ExtractResponse(BaseModel):
    title: str
    thumbnail: str
    duration: Optional[int]
    formats: List[VideoFormat]
    original_url: str
    extractor: str

@router.post("/extract", response_model=ExtractResponse)
async def extract_video_info(request: ExtractRequest):
    """
    Extract video metadata and direct download URLs from a given YouTube/Facebook link.
    """
    try:
        info = await downloader.extract_info(str(request.url))
        if not info:
            raise HTTPException(status_code=400, detail="Could not extract video information.")
        
        # Filter and structure the formats
        formats = []
        for f in info.get("formats", []):
            # We want formats that have video and audio combined, or at least have video
             if f.get("vcodec") != "none" and f.get("acodec") != "none":
                 # Only include if there's a direct URL
                 if f.get("url"):
                    formats.append(VideoFormat(
                        format_id=f.get("format_id", ""),
                        ext=f.get("ext", ""),
                        resolution=f.get("resolution", f.get("format_note", "unknown")),
                        filesize=f.get("filesize") or f.get("filesize_approx"),
                        url=f.get("url"),
                        vcodec=f.get("vcodec", "none"),
                        acodec=f.get("acodec", "none")
                    ))
        
        # Sort by resolution / quality (best first) - simple sort by resolution string if possible
        # or filesize
        formats.sort(key=lambda x: x.filesize or 0, reverse=True)
        
        # Limit to top 5 formats to keep the UI clean
        # Sometimes there are still duplicate resolutions
        unique_formats = []
        seen_res = set()
        for f in formats:
            if f.resolution not in seen_res:
                unique_formats.append(f)
                seen_res.add(f.resolution)

        return ExtractResponse(
            title=info.get("title", "Unknown Title"),
            thumbnail=info.get("thumbnail", ""),
            duration=info.get("duration"),
            formats=unique_formats[:6],
            original_url=str(request.url),
            extractor=info.get("extractor", "unknown")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
