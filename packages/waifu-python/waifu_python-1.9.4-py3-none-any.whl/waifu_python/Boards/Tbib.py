import random
import xml.etree.ElementTree as ET
from typing import Optional, List, Union

from ..Client.Client import client  
from ..API.api import TBIB_BASE_URL

class Tbib:
    @staticmethod
    async def fetch_images(
        tag: Optional[str] = None,
        limit: int = 1,
        max_retries: int = 10,
        use_proxy: bool = False,
        pid: Optional[int] = None
    ) -> Union[str, List[str], None]:
        params = {"limit": 1}
        if tag:
            params["tags"] = tag  

        attempt = 0
        while attempt < max_retries:
            try:
                count_resp = await client.get(TBIB_BASE_URL, params=params)
                count_resp.raise_for_status()
                if not count_resp.content:
                    attempt += 1
                    continue

                root = ET.fromstring(count_resp.content)
                total_count = int(root.attrib.get("count", 0))
                if total_count <= 0:
                    attempt += 1
                    continue
                
                per_page = 100
                total_pages = max((total_count + per_page - 1) // per_page, 1)
                selected_pid = random.randint(0, total_pages - 1)

                fetch_params = {"limit": per_page, "pid": selected_pid}
                if tag:
                    fetch_params["tags"] = tag
                
                fetch_resp = await client.get(TBIB_BASE_URL, params=fetch_params)
                fetch_resp.raise_for_status()
                if not fetch_resp.content:
                    attempt += 1
                    continue

                root = ET.fromstring(fetch_resp.content)
                posts = root.findall("post")
                if not posts:
                    attempt += 1
                    continue

                file_urls = [post.attrib.get("file_url") for post in posts if post.attrib.get("file_url")]
                if not file_urls:
                    attempt += 1
                    continue
                
                if limit == 1:
                    return random.choice(file_urls)
                return file_urls[:limit]

            except Exception as e:
                print(f"Error fetching images on attempt {attempt + 1}: {e}")
                attempt += 1
        return None

    @staticmethod
    async def fetch_sfw_images(
        tag: Optional[str] = None,
        limit: int = 1,
        max_retries: int = 10,
        use_proxy: bool = False
    ) -> Union[str, List[str], None]:
        parts: List[str] = []
        if tag:
            parts.append(tag.replace(" ", "_"))
        parts.append("rating:safe")
        combined = " ".join(parts)  
        return await Tbib.fetch_images(
            tag=combined,
            limit=limit,
            max_retries=max_retries,
            use_proxy=use_proxy
        )

    @staticmethod
    async def fetch_nsfw_images(
        tag: Optional[str] = None,
        limit: int = 1,
        max_retries: int = 10,
        use_proxy: bool = False
    ) -> Union[str, List[str], None]:
        parts: List[str] = []
        if tag:
            parts.append(tag.replace(" ", "_"))
        parts.append("rating:explicit")
        combined = " ".join(parts)
        return await Tbib.fetch_images(
            tag=combined,
            limit=limit,
            max_retries=max_retries,
            use_proxy=use_proxy
        )
