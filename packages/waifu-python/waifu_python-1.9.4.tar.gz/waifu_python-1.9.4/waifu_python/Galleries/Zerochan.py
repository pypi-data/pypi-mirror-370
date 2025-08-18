import random, httpx
import subprocess
import asyncio
from typing import Optional, Tuple, Union, List
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

from ..API.api import ZEROCHAN_BASE_URL
from ..Client.Client import client  

class Zerochan:
    USER_AGENT = "RaidenTG - RaidenShogun"
    MAX_REDIRECTS = 3
    GALLERY_DL_CMD = ["gallery-dl", "-q", "--get-urls", "-C", "cookies/zerochan.txt"]

    @staticmethod
    async def fetch_sfw_images(
        tag: Optional[str] = None,
        size: str = 'large',
        limit: int = 1
    ) -> Union[str, List[str], None]:
        """
        Fetch image(s) from Zerochan::
          1. Query the basic endpoint to get a list of posts (IDs).
          2. For each post, retrieve full post details to extract the post image link.
        """
        max_attempts = 4
        retrived_urls: List[str] = []
        attempt = 1

        while attempt <= max_attempts and len(retrived_urls) < limit:
            try:
                processed_tag, base_url, headers = Zerochan._prepare_request(tag)
                params = await Zerochan._get_random_params(client, processed_tag, headers)
                final_url, _ = await Zerochan._follow_redirects(client, base_url, params, headers)
                posts = await Zerochan._fetch_posts(client, final_url, params, headers)
                if not posts:
                    attempt += 1
                    continue

                random.shuffle(posts)
                for post in posts:
                    if len(retrived_urls) >= limit:
                        break
                    post_id = post.get('id')
                    if not post_id:
                        continue

                    image_url = await Zerochan._get_api_image_url(client, post_id, size, headers)
                    if not image_url:
                        
                        image_url = await Zerochan._get_gallerydl_image_url(post_id)
                    
                    if image_url and image_url not in retrived_urls:
                        retrived_urls.append(image_url)
            except Exception:                
                pass

            if len(retrived_urls) < limit:
                await asyncio.sleep(1)
            attempt += 1

        if not retrived_urls:
            return None
        return retrived_urls[0] if limit == 1 else retrived_urls

    @staticmethod
    async def _get_api_image_url(client, post_id: int, size: str, headers: dict) -> Optional[str]:
        """Try to get image URL through official API."""
        try:
            details_url = f"{ZEROCHAN_BASE_URL}/{post_id}?json"
            response = await client.get(details_url, headers=headers)
            response.raise_for_status()
            return response.json().get(size)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 303:
                print(f"API requires authentication for {post_id}, using fallback")
            return None
        except Exception as e:
            return None

    @staticmethod
    async def _get_gallerydl_image_url(post_id: int) -> Optional[str]:
        """Get image URL using gallery-dl fallback."""
        try:
            url = f"{ZEROCHAN_BASE_URL}/{post_id}"
            cmd = Zerochan.GALLERY_DL_CMD + [url]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=15
            )
            return result.stdout.strip().split('\n')[-1]
        except subprocess.CalledProcessError as e:
            print(f"Gallery-dl failed for post {post_id}: {e.stderr}")
            return None
        except Exception as e:
            print(f"Gallery-dl error for post {post_id}: {e}")
            return None
        
    @staticmethod
    async def _follow_redirects(client, url: str, params: dict, headers: dict) -> Tuple[str, dict]:
        current_url = url
        current_params = params.copy()
        redirect_count = 0

        while redirect_count < Zerochan.MAX_REDIRECTS:
            response = await client.get(current_url, params=current_params, headers=headers)
            if response.status_code not in (301, 302, 303, 307, 308):
                return current_url, current_params

            location = response.headers.get('Location')
            if not location:
                break

            parsed = urlparse(location)
            if not parsed.netloc:
                parsed = urlparse(current_url)._replace(path=location)
            
            existing_params = parse_qs(parsed.query)
            merged_params = {
                **existing_params,
                **{k: [str(v)] for k, v in current_params.items()}
            }
            merged_params.update({
                'json': [''],
                'l': [str(current_params.get('l', 100))],
                'p': [str(current_params.get('p', 1))]
            })
            current_url = urlunparse(parsed._replace(query=urlencode(merged_params, doseq=True)))
            redirect_count += 1

        return current_url, current_params

    @staticmethod
    async def _fetch_posts(client, url: str, params: dict, headers: dict) -> list:
        """Fetch and parse posts from API response."""
        try:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get('items', []) if isinstance(data, dict) else data
        except Exception as e:
            print(f"Fetch error: {e}")
            return []

    @staticmethod
    def _prepare_request(tag: Optional[str]) -> Tuple[str, str, dict]:
        if tag:
            tags = [t.strip().replace(" ", "+") for t in tag.split(",")]
            processed_tag = ",".join(tags)
        else:
            processed_tag = ""
        path = f"/{processed_tag}" if processed_tag else "/"
        headers = {"User-Agent": Zerochan.USER_AGENT, "Referer": ZEROCHAN_BASE_URL}
        return processed_tag, f"{ZEROCHAN_BASE_URL}{path}", headers

    @staticmethod
    async def _get_random_params(client, processed_tag: str, headers: dict) -> dict:
        """Generate random pagination parameters."""
        if processed_tag:
            return {'json': '', 'l': 100, 'p': random.randint(0, 10)}
        try:
            response = await client.get(f"{ZEROCHAN_BASE_URL}/?json", params={'json': '', 'l': 1}, headers=headers)
            if (data := response.json()) and (posts := data.get('items', data)):
                return {'json': '', 'l': 100, 'o': random.randint(1, posts[0]['id'])}
        except Exception:
            pass
        return {'json': '', 'l': 100}
