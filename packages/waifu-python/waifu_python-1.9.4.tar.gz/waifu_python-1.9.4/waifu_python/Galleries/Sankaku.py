import random
from typing import Optional, List

from ..API.api import SANKAKU_BASE_URL  
from ..Client.Client import client

class Sankaku:
    @staticmethod
    async def fetch_images(
        tag: Optional[str] = None,
        limit: int = 1,
        max_retries: int = 10,
        page_range: tuple = (1, 50)
    ) -> List[str]:
        """
          - If tag is provided: https://sankakuapi.com/posts?lang=en&page=<1-50>&limit=<1-100>&tags=<tag>
          - Otherwise:         https://sankakuapi.com/posts?page=<1-50>&limit=<1-100>
                  """
        fetch_limit = 100 if limit == 1 else limit

        params = {
            "limit": fetch_limit,
            "page": random.randint(page_range[0], page_range[1])
        }
        if tag:
            params["tags"] = tag

        attempt = 0
        while attempt < max_retries:
            try:
                response = await client.get(SANKAKU_BASE_URL, params=params)
                response.raise_for_status()
                posts = response.json()

                if not isinstance(posts, list):
                    attempt += 1
                    continue

                file_urls = [post["file_url"] for post in posts if post.get("file_url")]
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
        return await Sankaku.fetch_images(tag=combined_tag, limit=limit, max_retries=max_retries, page_range=(1, 50))

    @staticmethod
    async def fetch_nsfw_images(tag: Optional[str] = None, limit: int = 1, max_retries: int = 10) -> List[str]:
        """
        Fetch NSFW images with the 'rating:explict' filter.
        """
        nsfw_tag = "rating:explict"
        if tag:
            processed_tag = tag.replace(" ", "_")
            combined_tag = f"{processed_tag} {nsfw_tag}"
        else:
            combined_tag = nsfw_tag
        return await Sankaku.fetch_images(tag=combined_tag, limit=limit, max_retries=max_retries, page_range=(1, 50))
