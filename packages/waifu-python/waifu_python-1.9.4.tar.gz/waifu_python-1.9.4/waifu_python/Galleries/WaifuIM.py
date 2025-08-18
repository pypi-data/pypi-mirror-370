import random
from typing import Optional, Dict, Any, List

from ..API.api import WAIFUIM_BASE_URL
from ..Client.Client import client

class WaifuIm:
    @staticmethod
    async def fetch_images(tag: Optional[str] = None, limit: int = 1, is_nsfw: bool = False) -> List[str]:
        """
        Fetch images from waifu.im.
        """
        if is_nsfw:
            many = True
            original_limit = limit
            if limit == 1:
                limit = 2  
        else:
            many = True if limit > 1 else False
    
        params = {"many": many, "is_nsfw": is_nsfw}
        if limit > 1:
            params["limit"] = limit
    
        if tag:
            tag = tag.replace(" ", "-")
            params["included_tags"] = tag
    
        url = f"{WAIFUIM_BASE_URL}search"
    
        response = await client.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            images = [img["url"] for img in data.get("images", [])]
            
            if is_nsfw and original_limit == 1:
                return images[:1]
            return images
        raise Exception(f"Failed to fetch images: {response.text}")


    @staticmethod
    async def get_tags() -> Dict[str, Any]:
        """
        Fetch available tags from waifu.im API.
        """
        url = f"{WAIFUIM_BASE_URL}tags"
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to fetch tags: {response.text}")

    @staticmethod
    async def fetch_sfw_images(tag: Optional[str] = None, limit: int = 1) -> List[str]:
        """
        Fetch multiple SFW images from waifu.im API.
        If no tag is provided, a random tag is chosen from the 'versatile' category.
        """
        tags = await WaifuIm.get_tags()
        if "versatile" not in tags:
            return []

        tag = tag.replace(" ", "-") if tag else random.choice(tags["versatile"])
        return await WaifuIm.fetch_images(tag, limit, is_nsfw=False)

    @staticmethod
    async def fetch_nsfw_images(tag: Optional[str] = None, limit: int = 1) -> List[str]:
        """
        Fetch multiple NSFW images from waifu.im API.
        If no tag is provided, a random tag is chosen from the 'nsfw' category.
        """
        tags = await WaifuIm.get_tags()
        if "nsfw" not in tags:
            return []

        tag = tag.replace(" ", "-") if tag else random.choice(tags["nsfw"])
        return await WaifuIm.fetch_images(tag, limit, is_nsfw=True)
