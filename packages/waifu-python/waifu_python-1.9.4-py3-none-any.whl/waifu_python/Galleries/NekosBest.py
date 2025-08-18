import random
from typing import Optional, Union, List

from ..API.api import NEKOS_BASE_URL
from ..Client.Client import client

class NekosBest:
    tags = []

    @staticmethod
    async def get_tags() -> list:
        """Fetches all available tags from the endpoints API."""
        url = f"{NEKOS_BASE_URL}/endpoints"
        response = await client.get(url)
        if response.status_code == 200:
            NekosBest.tags = list(response.json().keys())
        else:
            NekosBest.tags = []
        return NekosBest.tags

    @staticmethod
    async def fetch_sfw_images(tag: Optional[str] = None, limit: int = 1) -> Union[str, List[str], None]:
        """
        Fetches images from nekos.best 
        """
        if not NekosBest.tags:
            await NekosBest.get_tags()

        tag = tag or random.choice(NekosBest.tags)
        url = f"{NEKOS_BASE_URL}/{tag}"
        
        fetched_urls = []
        max_attempts = 5
        attempts = 0
        while len(fetched_urls) < limit and attempts < max_attempts:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                images = data.get("results", [])
                for img in images:
                    image_url = img.get("url")
                    if image_url and image_url not in fetched_urls:
                        fetched_urls.append(image_url)
                    if len(fetched_urls) >= limit:
                        break
            attempts += 1

        if not fetched_urls:
            return None
        if limit == 1:
            return fetched_urls[0]
        else:
            return fetched_urls[:limit]

