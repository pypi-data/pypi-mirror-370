import random
import re
import json
from typing import Optional, Dict, Any, List

from ..Client.Client import client
from ..API.api import GRAPHQL_BASE_URL

class Anilist:
    @staticmethod
    async def get_characters(query: str, variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generic GraphQL fetch helper for character queries."""
        try:
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            response = await client.post(
                GRAPHQL_BASE_URL,
                headers=headers,
                json={"query": query, "variables": variables}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("Page", {}).get("characters", [])
        except Exception as e:
            print(f"Error fetching characters: {e}")
            return []

    @staticmethod
    async def get_characters_list(limit: int = 50, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch characters sorted by popularity, optionally filtered by search."""
        query = """
        query ($page: Int, $perPage: Int, $search: String) {
          Page(page: $page, perPage: $perPage) {
            characters(sort: FAVOURITES_DESC, search: $search) {
              id
              name { full }
              gender
              age
              description
              image { large }
              media { edges { node { title { romaji } } } }
            }
          }
        }
        """
        variables = {"page": 1, "perPage": limit, "search": search}
        return await Anilist.get_characters(query, variables)

    @staticmethod
    async def get_waifus(limit: int = 50, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch female characters (waifus)."""
        chars = await Anilist.get_characters_list(limit, search)
        return [c for c in chars if c.get("gender", "").lower() == "female"]

    @staticmethod
    def clean_description(description: str) -> str:
        """Clean up markdown/html from descriptions."""
        if not description:
            return "No description available."
        cleaned = re.sub(r'(<br>|\*\*|__)', '', description)
        return cleaned.strip()

    @staticmethod
    def _process_titles(titles: List[str]) -> str:
        """Simplify anime titles by removing common suffixes."""
        processed = [re.sub(r'\s*(?:Season|Part|Cour|Saga|Arc|:|\().*', '', t).strip() for t in titles]
        unique = list(dict.fromkeys(processed))
        return unique[0] if unique else titles[0]

    @staticmethod
    def _process_character(character: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize character data."""
        media = character.get("media", {}).get("edges", [])
        titles = list({m["node"]["title"]["romaji"] for m in media if m.get("node", {}).get("title")})
        anime_title = Anilist._process_titles(titles) if titles else "Unknown"
        return {
            "id": character["id"],
            "name": character["name"]["full"],
            "image": character["image"]["large"],
            "age": character.get("age", "Unknown"),
            "gender": character.get("gender", "Unknown"),
            "description": Anilist.clean_description(character.get("description", "")),
            "anime": anime_title
        }

    @staticmethod
    async def fetch_characters(count: int = 3, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return a random selection of characters."""
        chars = await Anilist.get_characters_list(search=search)
        if not chars:
            return []
        return [Anilist._process_character(c) for c in random.sample(chars, min(count, len(chars)))]

    @staticmethod
    async def fetch_waifus(count: int = 3, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return a random selection of female characters (waifus)."""
        waifus = await Anilist.get_waifus(search=search)
        if not waifus:
            return []
        return [Anilist._process_character(w) for w in random.sample(waifus, min(count, len(waifus)))]

    @staticmethod
    async def fetch_anime_by_id(anime_id: int) -> Optional[Dict[str, Any]]:
        """Fetch detailed anime data by ID."""
        query = """
        query ($id: Int) {
          Media(id: $id, type: ANIME) {
            id
            title { romaji english native }
            studios { nodes { name } }
            averageScore
            genres
            episodes
            status
            format
            startDate { year month day }
            tags { name }
            description
            relations {
              edges {
                relationType
                node {
                  id
                  title { romaji english native }
                  averageScore
                  episodes
                  status
                  description
                  format
                }
              }
            }
          }
        }
        """
        variables = {"id": anime_id}
        try:
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            resp = await client.post(GRAPHQL_BASE_URL, headers=headers, json={"query": query, "variables": variables})
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}).get("Media")
        except Exception as e:
            print(f"Error fetching anime by ID: {e}")
            return None

    @staticmethod
    async def get_anime(
        search: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for anime titles by name, include relations, and thumbnails."""
        query = """
        query ($page: Int, $perPage: Int, $search: String) {
          Page(page: $page, perPage: $perPage) {
            media(search: $search, type: ANIME) {
              id
              title { romaji english native }
              studios { nodes { name } }
              averageScore
              genres
              episodes
              status
              format
              startDate { year month day }
              description
              relations {
                edges {
                  relationType
                  node { id title { romaji english native } }
                }
              }
            }
          }
        }
        """
        variables = {"page": 1, "perPage": limit, "search": search}
        try:
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            resp = await client.post(
                GRAPHQL_BASE_URL,
                headers=headers,
                json={"query": query, "variables": variables}
            )
            resp.raise_for_status()
            data = resp.json()
            raw_list = data["data"]["Page"]["media"]

            for anime in raw_list:
                anime["thumbnail"] = f"https://img.anili.st/media/{anime['id']}"
                rels = anime.get("relations", {}).get("edges", [])
                anime["relations"] = [
                    {
                        "type": edge["relationType"],
                        "id": edge["node"]["id"],
                        "title": edge["node"]["title"],
                        "thumbnail": f"https://img.anili.st/media/{edge['node']['id']}"
                    }
                    for edge in rels
                ]

            return raw_list

        except Exception as e:
            print(f"Error searching anime: {e}")
            return []

    @staticmethod
    async def search_anime(
        search: str,
        limit: int = 10
    ) -> str:
        """returns a pretty‑printed JSON string."""
        result = await Anilist.get_anime(search=search, limit=limit)
        return json.dumps({"result": result}, indent=2, ensure_ascii=False)