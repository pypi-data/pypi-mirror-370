import random
from typing import Optional, List, Union

from ..API.api import SAFEBORRU_BASE_URL
from ..Client.Client import client

class Safebooru:
    @staticmethod
    async def fetch_images(tag: Optional[str] = None, limit: int = 1) -> Union[str, List[str], None]:
        """
        Fetch image URLs from SafeBooru API.
        """
        if limit == 1:
            request_limit = 100
            pid = random.randint(0, 50)
        else:
            request_limit = limit
            pid = None

        params = {
            "page": "dapi",
            "s": "post",
            "q": "index",
            "json": 1,
            "limit": request_limit,
        }
        if pid is not None:
            params["pid"] = pid

        if tag:
            params["tags"] = tag.replace(" ", "_")

        try:
            response = await client.get(SAFEBORRU_BASE_URL, params=params)
            response.raise_for_status()
            images = response.json()
            file_urls = [
                f"https://safebooru.org/images/{img['directory']}/{img['image']}"
                for img in images if "image" in img and "directory" in img
            ]
            if not file_urls:
                return None

            if limit == 1:
                return random.choice(file_urls)
            else:
                return file_urls[:limit]
        except Exception as e:
            print(f"Error fetching images: {e}")
            return None
