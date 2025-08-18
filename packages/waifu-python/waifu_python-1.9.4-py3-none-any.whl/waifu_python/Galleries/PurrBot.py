import random
from typing import Optional, Dict, Any, Union, List

from ..API.api import PURRBOT_BASE_URL
from ..Client.Client import client

class PurrBot:
    purrbot_nsfw_tags = [
        "anal", "blowjob", "cum", "fuck", "pussylick", "solo", "solo_male",
        "threesome_fff", "threesome_ffm", "threesome_mmf", "yaoi", "yuri", "neko"
    ]
    
    purrbot_tags = ["eevee", "holo", "icon", "kitsune", "neko", "okami", "senko", "shiro"]

    purrbot_reactions = [
        "angry", "bite", "blush", "comfy", "cry", "cuddle", "dance", "fluff",
        "hug", "kiss", "lay", "lick", "pat", "neko", "poke", "pout", "slap", 
        "smile", "tail", "tickle", "eevee"
    ]

    @staticmethod
    async def get_tags() -> Dict[str, Any]:
        """Return a dictionary of SFW and NSFW tags."""
        return {
            "sfw": PurrBot.purrbot_tags + PurrBot.purrbot_reactions,
            "nsfw": PurrBot.purrbot_nsfw_tags
        }

    @staticmethod
    async def fetch_purrbot_sfw(tag: Optional[str] = None, limit: int = 1) -> List[str]:
        """
        Fetch multiple SFW images/gifs
        """
        results = []
        for _ in range(limit):
            func = random.choice([PurrBot.fetch_sfw_images, PurrBot.fetch_sfw_gif])
            from inspect import signature
            sig = signature(func)
            kwargs = {}
            if 'tag' in sig.parameters:
                kwargs['tag'] = tag
            
            res = await func(**kwargs)
            
            if isinstance(res, dict):
                results.append(res.get('link', res.get('error', 'Unknown error')))
            else:
                results.append(res)
        return results

    @staticmethod
    async def fetch_sfw_gif(tag: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch a SFW gif from purrbot.site 
        """
        
        reaction = random.choice(PurrBot.purrbot_reactions)
        if reaction not in PurrBot.purrbot_reactions:
            return {"error": "Invalid reaction"}
        
        if not tag:
            tag = random.choice(PurrBot.purrbot_reactions)
        else:
            tag = tag.replace(" ", "_")
        
        if tag not in (PurrBot.purrbot_reactions + PurrBot.purrbot_tags):
            return {"error": "Invalid tag"}
    
        url = f"{PURRBOT_BASE_URL}/img/sfw/{reaction}/gif"
        params = {"tag": tag}
    
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("link") or {"error": "No link found"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    async def fetch_nsfw_gif(tag: Optional[str] = None, limit: int = 1) -> List[str]:
        """
        Fetch NSFW gifs and return a list of URLs in the same format as SFW fetches.
        """
        results: List[str] = []
        provided_tag = tag.replace(" ", "_") if tag else None
        max_attempts = limit * 3
        attempts = 0
    
        while len(results) < limit and attempts < max_attempts:
            current_tag = provided_tag if provided_tag is not None else random.choice(PurrBot.purrbot_nsfw_tags)
            if current_tag not in PurrBot.purrbot_nsfw_tags:
                attempts += 1
                continue
    
            url = f"{PURRBOT_BASE_URL}/img/nsfw/{current_tag}/gif"
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                result = data.get("link") or {"error": "No link found"}
                
                if isinstance(result, str) and result not in results:
                    results.append(result)
                elif isinstance(result, dict) and "error" not in result:
                    link = result.get("link")
                    if link and link not in results:
                        results.append(link)
            except Exception:
                pass
    
            attempts += 1
    
        if not results:
            return ["Failed to fetch NSFW GIF"]
        return results
    

    @staticmethod
    async def fetch_sfw_images(tag: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch a SFW image.
        """
        if not tag:
            tag = random.choice(PurrBot.purrbot_tags)
        else:
            tag = tag.replace(" ", "_")
        
        if tag not in PurrBot.purrbot_tags:
            return {"error": "Invalid tag"}
        
        url = f"{PURRBOT_BASE_URL}/img/sfw/{tag}/img"
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("link") or {"error": "No link found"}
        except Exception as e:
            return {"error": str(e)}
