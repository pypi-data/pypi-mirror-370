import random
from typing import Optional, List

from ..API.api import DANBORRU_BASE_URL
from ..Client.Client import client, DEFAULT_HEADERS

class Danbooru:
    @staticmethod
    async def fetch_images(tag: Optional[str] = None,limit: int = 1,max_retries: int = 10,page_range: tuple = (0, 50)) -> List[str]:
        """
        Fetch image URLs from Danbooru.
        """
        request_limit = 200 if limit == 1 else min(limit, 200)
        params = {"limit": request_limit}
        if tag:
            params["tags"] = tag
        params["page"] = random.randint(page_range[0], page_range[1])

        attempt = 0
        while attempt < max_retries:
            try:
                response = await client.get(DANBORRU_BASE_URL, params=params, headers=DEFAULT_HEADERS)
                response.raise_for_status()
                images = response.json()

                if not isinstance(images, list):
                    attempt += 1
                    continue

                file_urls = [img["file_url"] for img in images if "file_url" in img and img["file_url"]]
                if not file_urls:
                    attempt += 1
                    continue

                if limit == 1:
                    return [random.choice(file_urls)]
                else:
                    return file_urls[:limit]
            except Exception:
                attempt += 1
        return []

    @staticmethod
    async def fetch_sfw_images(tag: Optional[str] = None, limit: int = 1, max_retries: int = 10) -> List[str]:
        """
        Fetch SFW images with the 'rating:safe' filter.
        """
        safe_tag = "rating:safe"
        if tag:
            processed_tag = tag.replace(" ", "_")
            combined_tag = f"{processed_tag} {safe_tag}"
        else:
            combined_tag = safe_tag
        return await Danbooru.fetch_images(tag=combined_tag, limit=limit, max_retries=max_retries, page_range=(0, 50))

    @staticmethod
    async def fetch_nsfw_images(tag: Optional[str] = None, limit: int = 1, max_retries: int = 10) -> List[str]:
        """
        Fetch NSFW images with the 'rating:explicit' filter.
        """
        nsfw_tag = "rating:explicit"
        if tag:
            processed_tag = tag.replace(" ", "_")
            combined_tag = f"{processed_tag} {nsfw_tag}"
        else:
            combined_tag = nsfw_tag
        return await Danbooru.fetch_images(tag=combined_tag, limit=limit, max_retries=max_retries, page_range=(0, 15))