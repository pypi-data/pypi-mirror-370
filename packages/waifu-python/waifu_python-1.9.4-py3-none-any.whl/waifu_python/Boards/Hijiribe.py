import random
import urllib.parse
from typing import List, Optional

from ..Client.Client import client
from ..API.api import HIJIRIBE_BASE_URL

class Hijiribe:
    @staticmethod
    def _build_query(tags: List[str], page: int) -> str:
        """Handle Query's"""
        
        processed = [t.replace(" ", "_") for t in tags]
        joined = "+".join(processed)
        encoded = urllib.parse.quote(joined, safe=":+")
        return f"tags={encoded}&page={page}&limit=200"

    @staticmethod
    async def fetch_images(
        tags: Optional[List[str]] = None,
        limit: int = 1,
        max_retries: int = 10,
        page_range: Optional[tuple] = None
    ) -> List[str]:
        tags = tags or []
        collected = []
        seen_pages = set()
        final_page_range = page_range or ((1, 1000) if not tags else (1, 20))

        for attempt in range(max_retries):
            
            while True:
                page = random.randint(final_page_range[0], final_page_range[1])
                if page not in seen_pages:
                    seen_pages.add(page)
                    break
            try:
                query = Hijiribe._build_query(tags, page)
                full_url = f"{HIJIRIBE_BASE_URL}?{query}"
                response = await client.get(full_url)
                response.raise_for_status()
                posts = response.json()

                urls = [
                    p["file_url"] for p in posts
                    if isinstance(p, dict) and p.get("file_url")
                ]

                if urls:
                    collected.extend(urls)
                    if len(collected) >= limit:
                        return random.sample(collected, limit)
            except Exception:
                continue
        return random.sample(collected, min(limit, len(collected)))

    @staticmethod
    async def fetch_sfw_images(
        tag: Optional[str] = None,
        limit: int = 1,
        max_retries: int = 10
    ) -> List[str]:
        tags: List[str] = ["rating:safe"]
        if tag:
            tags.append(tag)
        return await Hijiribe.fetch_images(
            tags=tags,
            limit=limit,
            max_retries=max_retries,
            
            page_range=(1, 10)
        )

    @staticmethod
    async def fetch_nsfw_images(
        tag: Optional[str] = None,
        limit: int = 1,
        max_retries: int = 10
    ) -> List[str]:
        tags: List[str] = []
        if tag:
            tags.extend([tag, "rating:explicit"])
        return await Hijiribe.fetch_images(
            tags=tags,
            limit=limit,
            max_retries=max_retries,
            page_range=(1, 20) if tag else None
        )
