import os
import hashlib
import httpx
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

from ..API.api import IWARA_API_URL

load_dotenv()

EMAIL = os.getenv("IWARA_EMAIL")
PASSWORD = os.getenv("IWARA_PASSWORD")

class Iwara:
    _client: Optional[httpx.AsyncClient] = None

    @classmethod
    async def _ensure_client(cls) -> httpx.AsyncClient:
        if cls._client is None:
            if not EMAIL or not PASSWORD:
                raise ValueError("IWARA_EMAIL and IWARA_PASSWORD must be set in .env")
            temp = httpx.AsyncClient(timeout=30.0)
            resp = await temp.post(
                f"{IWARA_API_URL}/user/login",
                json={"email": EMAIL, "password": PASSWORD}
            )
            resp.raise_for_status()
            token = resp.json().get("token")
            await temp.aclose()
            if not token:
                raise RuntimeError("Login failed: no token returned")
            
            cls._client = httpx.AsyncClient(
                timeout=30.0,
                headers={"Authorization": f"Bearer {token}"}
            )
        return cls._client

    @classmethod
    async def get_videos(
        cls,
        sort: str = "date",
        rating: str = "all",
        page: int = 0,
        limit: int = 32,
        subscribed: bool = False,
    ) -> Dict[str, Any]:
        """List videos; returns parsed JSON."""
        client = await cls._ensure_client()
        params = {
            "sort": sort,
            "rating": rating,
            "page": page,
            "limit": limit,
            "subscribed": str(subscribed).lower()
        }
        resp = await client.get(f"{IWARA_API_URL}/videos", params=params)
        resp.raise_for_status()
        return resp.json()

    @classmethod
    async def get_video(cls, video_id: str) -> Dict[str, Any]:
        """Fetch metadata for a single video."""
        client = await cls._ensure_client()
        resp = await client.get(f"{IWARA_API_URL}/video/{video_id}")
        resp.raise_for_status()
        return resp.json()

    @classmethod
    async def get_download_resources(cls, video_id: str) -> List[Dict[str, Any]]:
        """Return raw JSON list of download resources."""
        meta = await cls.get_video(video_id)
        signed_url = meta["fileUrl"]
        
        file_id = signed_url.split("/")[4]
        expires = signed_url.split("?")[1].split("&")[0].split("=")[1]
        sha_postfix = "_5nFp9kmbNnHdAFhaqMvt"
        key = f"{file_id}_{expires}{sha_postfix}"
        version_hash = hashlib.sha1(key.encode()).hexdigest()
        headers = {"X-Version": version_hash}

        client = await cls._ensure_client()
        resp = await client.get(signed_url, headers=headers)
        resp.raise_for_status()
        return resp.json()

    @classmethod
    async def fetch_details(cls, video_id: str) -> Dict[str, Any]:
        """Full metadata + download URLs for given video."""
        metadata = await cls.get_video(video_id)
        resources = await cls.get_download_resources(video_id)
        return {"metadata": metadata, "resources": resources}

    @classmethod
    async def iwara_fetch(
        cls,
        sort: str = "date",
        rating: str = "all",
        page: int = 0,
        limit: int = 1,
        subscribed: bool = False,
    ) -> Dict[str, List[str]]:
        """
        :param sort: sort order (date, trending, popularity, views, likes)
        :param rating: content rating (all, general, ecchi)
        :param page: starts from 0 page index
        :param limit: number of videos per page
        :param subscribed: whether to filter subscribed videos
        :return: dict where keys are video IDs and values are lists of full download URLs
        """
        page_data = await cls.get_videos(
            sort=sort,
            rating=rating,
            page=page,
            limit=limit,
            subscribed=subscribed
        )
        results = page_data.get("results", [])
        output: Dict[str, List[str]] = {}
        for video in results:
            vid = video.get("id")
            resources = await cls.get_download_resources(vid)
            urls = ["https:" + r.get("src", {}).get("download", "") for r in resources if r.get("src", {}).get("download")]
            output[vid] = urls
        return output

#    @classmethod
#    async def fetch_random_video(
#        cls,
#        sort: str = "date",
#        rating: str = "all",
#        subscribed: bool = False,
#        limit: int = 32,
#    ) -> Dict[str, Any]:
#        first = await cls.get_videos(sort=sort, rating=rating, page=0, limit=limit, subscribed=subscribed)
#        total = first.get("count", 0)
#        if not total:
#            raise ValueError("No videos found")
#        total_pages = math.ceil(total / limit)
#        rand_page = random.randrange(total_pages)
#        page_data = await cls.get_videos(sort=sort, rating=rating, page=rand_page, limit=limit, subscribed=subscribed)
#        choices = page_data.get("results", [])
#        if not choices:
#            raise RuntimeError(f"No results on page {rand_page}")
#        return random.choice(choices)

    @classmethod
    async def fetch_random(
        cls,
        sort: str = "date",
        rating: str = "all",
        subscribed: bool = False,
        limit: int = 1,
    ) -> Dict[str, Any]:
        rand_meta = await cls.fetch_random_video(sort=sort, rating=rating, subscribed=subscribed, limit=limit)
        return await cls.fetch_details(rand_meta['id'])
