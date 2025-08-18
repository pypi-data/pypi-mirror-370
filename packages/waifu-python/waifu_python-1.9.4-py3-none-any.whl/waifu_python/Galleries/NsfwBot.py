import random
from typing import Dict, Any, Optional, Union, List

from ..API.api import NSFWBOT_BASE_URL
from ..Client.Client import client

class NSFWBot:
    @staticmethod
    async def get_tags() -> Dict[str, Any]:
        """Fetch available SFW and NSFW tags."""
        url = f"{NSFWBOT_BASE_URL}/endpoints"
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching tags: {e}")
            return {"error": str(e)}

    @staticmethod
    async def _fetch_image(endpoint_type: str, tag: str) -> Optional[str]:
        """Fetch an image and return only the 'url_cdn' value."""
        tag = tag.replace(" ", "-")
        url = f"{NSFWBOT_BASE_URL}/{endpoint_type}/{tag.lower()}"
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("url_cdn")
        except Exception as e:
            print(f"Error fetching tag '{tag}' ({endpoint_type}): {e}")
            return None

    @staticmethod
    async def fetch_sfw_images(tag: Optional[str] = None, limit: int = 1) -> Union[str, List[str], None]:
        """
        Fetch SFW image(s) from NSFWBot.
        """
        tags = await NSFWBot.get_tags()
        if "sfw" not in tags or not tags["sfw"]:
            return {"error": "No available SFW tags."}

        tag = tag or random.choice(tags["sfw"])
        retrived_urls: List[str] = []
        max_attempts = limit * 3  
        attempts = 0
        while len(retrived_urls) < limit and attempts < max_attempts:
            result = await NSFWBot._fetch_image("sfw", tag)
            if result and result not in retrived_urls:
                retrived_urls.append(result)
            attempts += 1

        if not retrived_urls:
            return {"error": "Failed to fetch SFW image."}
        if limit == 1:
            return retrived_urls[0]
        return retrived_urls[:limit]

    @staticmethod
    async def fetch_nsfw_images(tag: Optional[str] = None, limit: int = 1) -> Union[str, List[str], None]:
        """
        Fetch NSFW image(s) from NSFWBot.
        """
        tags = await NSFWBot.get_tags()
        if "nsfw" not in tags or not tags["nsfw"]:
            return {"error": "No available NSFW tags."}

        tag = tag or random.choice(tags["nsfw"])
        retrived_urls: List[str] = []
        max_attempts = limit * 3
        attempts = 0
        while len(retrived_urls) < limit and attempts < max_attempts:
            result = await NSFWBot._fetch_image("nsfw", tag)
            if result and result not in retrived_urls:
                retrived_urls.append(result)
            attempts += 1

        if not retrived_urls:
            return {"error": "Failed to fetch NSFW image."}
        if limit == 1:
            return retrived_urls[0]
        return retrived_urls[:limit]
