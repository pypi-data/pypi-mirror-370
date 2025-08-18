import random
from typing import Optional, List, Union, Any

from ..API.api import GELBORRU_BASE_URL
from ..Client.Client import client

class Gelbooru:
    MAX_RETRIES = 10  

    @staticmethod
    async def fetch_images(tag: Optional[str] = None, limit: int = 100) -> Union[str, List[str], None]:
        """
        Fetch random SFW image(s) from Gelbooru API.
        """
        total_posts = await Gelbooru._get_total_posts(client, tag)
        if not total_posts:
            return None  
        if tag:
            max_pages = max(total_posts // limit, 1)
        else:
            max_pages = 200

        for _ in range(Gelbooru.MAX_RETRIES):
            try:
                params = Gelbooru._prepare_request(tag, limit, max_pages)
                posts = await Gelbooru._fetch_posts(client, params)
                if posts:
                    
                    valid_posts = [post for post in posts if post.get('file_url')]
                    if valid_posts:
                        if limit == 1:
                            return random.choice(valid_posts).get('file_url')
                        else:
                            sample_size = min(limit, len(valid_posts))
                            selected_posts = random.sample(valid_posts, sample_size)
                            return [post.get('file_url') for post in selected_posts]
            except Exception:
                
                pass  
        return None  

    @staticmethod
    async def _get_total_posts(client: Any, tag: Optional[str]) -> int:
        """
        Fetch the total number of available posts for a given tag.
        """
        try:
            params = {
                'page': 'dapi',
                's': 'post',
                'q': 'index',
                'json': '1',
                'limit': 1  
            }
            if tag:
                params['tags'] = tag.replace(' ', '_')

            response = await client.get(GELBORRU_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            count = int(data.get('@attributes', {}).get('count', 0))
            return count
        except Exception:
            return 0  

    @staticmethod
    async def _fetch_posts(client: Any, params: dict) -> List[Any]:
        """
        Fetch and parse posts from Gelbooru API using the given parameters.
        """
        try:
            response = await client.get(GELBORRU_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('post', []) if isinstance(data, dict) else []
        except Exception:
            return []

    @staticmethod
    def _prepare_request(tag: Optional[str], limit: int, max_pages: int) -> dict:
        """
        Prepare API request parameters with dynamic pagination.
        """
        base_params = {
            'page': 'dapi',
            's': 'post',
            'q': 'index',
            'json': '1',
            'limit': limit,
            'pid': random.randint(0, max_pages - 1)
        }
        if tag:
            base_params['tags'] = tag.replace(' ', '_')
        return base_params
