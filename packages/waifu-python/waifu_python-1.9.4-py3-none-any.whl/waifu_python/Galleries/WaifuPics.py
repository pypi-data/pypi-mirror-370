import random
from typing import Optional, Dict, Any, List, Union

from ..API.api import WAIFUPICS_BASE_URL
from ..Client.Client import client

class WaifuPics:
    @staticmethod
    async def get_tags() -> Optional[Dict[str, Any]]:
        """Fetches all available tags from the /endpoints API."""
        url = f"{WAIFUPICS_BASE_URL}/endpoints"
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching tags: {e}")
            return None

    @staticmethod
    async def fetch_sfw_images(
        tag: Optional[str] = None, 
        limit: int = 1, 
        type: str = "sfw"
    ) -> Union[str, List[str], None]:
        """
        Fetches SFW images.
        """
        type = type.lower()
        tags = await WaifuPics.get_tags()
        if tags is None or type not in tags:
            return None
        
        results = []
        for _ in range(limit):
            chosen_tag = tag or (random.choice(tags[type]) if tags[type] else None)
            if not chosen_tag:
                continue

            url = f"{WAIFUPICS_BASE_URL}/{type}/{chosen_tag}"
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                img_url = data.get("url")
                if img_url:
                    results.append(img_url)
            except Exception as e:
                print(f"Error fetching SFW image: {e}")
        
        if not results:
            return None
        return results[0] if limit == 1 else results

    @staticmethod
    async def fetch_nsfw_images(
        tag: Optional[str] = None, 
        limit: int = 1, 
        type: str = "nsfw"
    ) -> Union[str, List[str], None]:
        """
        Fetches NSFW images.
        """
        type = type.lower()
        tags = await WaifuPics.get_tags()
        if tags is None or type not in tags:
            return None
        
        results = []
        for _ in range(limit):
            chosen_tag = tag or (random.choice(tags[type]) if tags[type] else None)
            if not chosen_tag:
                continue

            url = f"{WAIFUPICS_BASE_URL}/{type}/{chosen_tag}"
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                img_url = data.get("url")
                if img_url:
                    results.append(img_url)
            except Exception as e:
                print(f"Error fetching NSFW image: {e}")
        
        if not results:
            return None
        return results[0] if limit == 1 else results
