import aiohttp, traceback, asyncio, orjson
from ..Config import Config

class BasicInformation:
    @staticmethod
    async def get(ouid: str) -> dict:
        """Method to fetch basic information for a given username.

        Args:
            ouid (str): The ouid to fetch information for.

        Raises:
            Exception: If the API request fails or the username is invalid.

        Returns:
            dict: The basic information associated with the username.
        """
        cfg = Config.get()
        url = f"https://open.api.nexon.com/tfd/v1/user/basic?ouid={ouid}"
        headers = {
            "x-nxopen-api-key": cfg.api_key,
            "accept": "application/json"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    if cfg.debug:
                        traceback.print_exc()
                    raise Exception(f"Error fetching basic information: {response.status} - {response.reason}")
    
    @staticmethod
    async def get_formatted(ouid: str) -> str:
        """Get basic information and format's it for easier Reading, Displaying and Usage.

        Args:
            ouid (str): OUID of the user.

        Raises:
            Exception: If the API request fails or the Uoid / username is invalid.

        Returns:
            str: Formatted json. 
        """
        cfg = Config.get()
        language = cfg.language or "en"
        base_url = "https://open.api.nexon.com"
        headers = {
            "x-nxopen-api-key": cfg.api_key,
            "accept": "application/json"
        }
        
        async def fetch_json(session, url, headers=None):
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    raw = await response.read()
                    return orjson.loads(raw)
                if cfg.debug:
                    traceback.print_exc()
                raise Exception(f"Error fetching {url}: {response.status} - {response.reason}")

        async with aiohttp.ClientSession() as session:
            data, titles, medals = await asyncio.gather(
                fetch_json(session, f"{base_url}/tfd/v1/user/basic?ouid={ouid}", headers),
                fetch_json(session, f"{base_url}/static/tfd/meta/{language}/title.json"),
                fetch_json(session, f"{base_url}/static/tfd/meta/{language}/medal.json")
            )
        
        # Looks through /static/tfd/meta/{language}/title.json
        prefix = next((t["title_name"] for t in titles if t["title_id"] == str(data.get("title_prefix_id"))), "")
        suffix = next((t["title_name"] for t in titles if t["title_id"] == str(data.get("title_suffix_id"))), "")
        title = " ".join(filter(None, [prefix, suffix]))
        
        # Same as above but for medals.
        medal_id = str(data.get("medal_id"))
        medal_level = data.get("medal_level")
        medal_name, medal_image = "", ""

        medal_entry = next((m for m in medals if m["medal_id"] == medal_id), None)
        if medal_entry:
            detail = next((d for d in medal_entry.get("medal_detail", []) if d["medal_level"] == medal_level), None)
            if detail:
                medal_name = detail.get("medal_name", "")
                medal_image = detail.get("medal_image_url", "")
                medal_tier_id = detail.get("medal_tier_id", "")
                medal_level = detail.get("medal_level", "")
        
        return {
            # Might have to add default values.
            "ouid": ouid,
            "username": data.get("user_name"),
            "platform": data.get("platform_type"),
            "mastery_rank": data.get("mastery_rank_level"),
            "mastery_rank_xp": data.get("mastery_rank_exp"),
            "prefix": prefix,
            "suffix": suffix,
            "prefix_id": data.get("title_prefix_id"),
            "suffix_id": data.get("title_suffix_id"),
            "title": title,
            "os_language": data.get("os_language"),
            "game_language": data.get("game_language"),
            "medal_id": data.get("medal_id"),
            "medal_name": medal_name,
            "medal_image": medal_image,
            "medal_tier_id": medal_tier_id,
            "medal_level": medal_level,
        }