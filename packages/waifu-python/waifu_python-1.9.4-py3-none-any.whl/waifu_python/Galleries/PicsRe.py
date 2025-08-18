import random
from typing import Optional, List, Dict, Any, Union

from ..API.api import PICRE_BASE_URL
from ..Client.Client import client

class PicRe:
    @staticmethod
    async def get_tags() -> Dict[str, Any]:
        """Fetch available tags from pic.re API."""
        url = f"{PICRE_BASE_URL}tags"
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching tags: {e}")
            return {}

    @staticmethod
    async def fetch_sfw_images(tags: Optional[List[str]] = None, limit: int = 1) -> Union[str, List[str], None]:
        """
        Fetch safe-for-work images
        """
        params = {}
        if tags:
            params["in"] = ",".join(tag.replace(" ", "_") for tag in tags)
        
        url = f"{PICRE_BASE_URL}image.json"
        
        retrived_urls: List[str] = []
        max_attempts = limit * 3  
        attempts = 0
        
        while len(retrived_urls) < limit and attempts < max_attempts:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                image_url = data.get("file_url")
                if image_url:
                    if not image_url.startswith("http"):
                        image_url = "https://" + image_url
                    if image_url not in retrived_urls:
                        retrived_urls.append(image_url)
            except Exception:
                pass
            attempts += 1

        if not retrived_urls:
            return None
        if limit == 1:
            return retrived_urls[0]
        return retrived_urls[:limit]
