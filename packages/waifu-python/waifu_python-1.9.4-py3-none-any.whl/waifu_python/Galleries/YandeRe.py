import httpx
import random
from typing import Optional, List

from ..Client.Client import client 
from ..API.api import YANDE_RE_BASE_URL

class Yandere:
    @staticmethod
    async def fetch_images(tag: Optional[str] = None, limit: int = 1, max_retries: int = 15) -> List[str]:
        params = {"limit": 1000} if limit == 1 else {"limit": limit}
        if tag:
            params["tags"] = tag.replace(" ", "_") 
            
        for _ in range(max_retries):
            try:
                response = await client.get(YANDE_RE_BASE_URL, params=params)
                response.raise_for_status()
                if not response.content:
                    continue
                images = response.json()
                if not isinstance(images, list):
                    continue
                file_urls = [img["file_url"] for img in images if "file_url" in img]
                if limit == 1:
                    return [random.choice(file_urls)] if file_urls else []
                else:
                    return file_urls[:limit]
            except (httpx.HTTPStatusError, httpx.RequestError, ValueError):
                continue
        return []
