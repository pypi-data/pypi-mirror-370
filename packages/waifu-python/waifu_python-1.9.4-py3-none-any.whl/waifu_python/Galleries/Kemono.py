import random
from typing import Optional, List, Union, Dict, Any

from ..Client.Client import client 
from ..API.api import KEMONO_BASE_URL

class KemonoParty:
    @staticmethod
    async def fetch_posts(tag: Optional[str] = None, limit: int = 100) -> List[dict]:
        """
        Fetch posts from Kemono Party API based on a tag.
        Each post's 'file' and 'attachments' fields will have a new key 'full_url'
        containing the complete URL, constructed by prefixing the KEMONO_BASE_URL.
        """
        params = {"limit": limit}
        if tag:
            params["tag"] = tag.replace(" ", "_")

        url = f"{KEMONO_BASE_URL}/api/v1/posts"
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            posts = data.get("posts", [])
            
            for post in posts:
                if "file" in post and isinstance(post["file"], dict) and "path" in post["file"]:
                    post["file"]["full_url"] = f"{KEMONO_BASE_URL}{post['file']['path']}"
                
                if "attachments" in post and isinstance(post["attachments"], list):
                    for attachment in post["attachments"]:
                        if "path" in attachment:
                            attachment["full_url"] = f"{KEMONO_BASE_URL}{attachment['path']}"
            return posts
        except Exception as e:
            print(f"Error fetching posts: {e}")
            return []

    @staticmethod
    def is_valid_post(post: dict) -> bool:
        """
        Check if a post has a valid preview file and at least one valid attachment.
        """
        if "file" not in post or not isinstance(post["file"], dict) or not post["file"].get("path"):
            return False
        if "attachments" not in post or not isinstance(post["attachments"], list) or len(post["attachments"]) == 0:
            return False
        if not any(attachment.get("path") for attachment in post["attachments"]):
            return False
        return True

    @staticmethod
    def _extract_result(post: dict) -> Dict[str, Any]:
        """
        Build a result dictionary from a valid post.
        Includes the main file full_url and a list of attachment full_urls.
        """
        result = {}
        file_url = post.get("file", {}).get("full_url")
        attachments = [att.get("full_url") for att in post.get("attachments", []) if att.get("full_url")]
        result["file"] = file_url
        result["attachments"] = attachments
        return result

    @staticmethod
    async def fetch_nsfw_images(tag: Optional[str] = None, limit: int = 1) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """
        Fetch NSFW images
        """
        posts = await KemonoParty.fetch_posts(tag=tag, limit=100)
        valid_posts = [post for post in posts if KemonoParty.is_valid_post(post)]
        if not valid_posts:
            return None
        
        if limit == 1:
            chosen_post = random.choice(valid_posts)
            return KemonoParty._extract_result(chosen_post)
        else:
            sample_size = min(limit, len(valid_posts))
            selected_posts = random.sample(valid_posts, sample_size)
            return [KemonoParty._extract_result(post) for post in selected_posts]
