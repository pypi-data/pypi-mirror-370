import aiohttp, orjson, traceback
from urllib.parse import quote_plus
from .Config import Config
from .exceptions import InvalidOUID

class Uoid:
	@staticmethod
	async def get(username: str) -> str:
		"""Method to fetch the OUID for a given username.

		Args:
			username (str): The username to fetch the OUID for.

		Raises:
			InvalidOUID: If the username is invalid or the API request fails.

		Returns:
			str: The OUID associated with the username.
		"""
		cfg = Config.get()
		modified_name = quote_plus(username)
		url = f"https://open.api.nexon.com/tfd/v1/id?user_name={modified_name}"
		headers = {
			"x-nxopen-api-key": cfg.api_key,
			"accept": "application/json"
		}
		async with aiohttp.ClientSession() as session:
			async with session.get(url, headers=headers) as response:
				if response.status == 200:
					data = await response.json()
					return data.get("ouid")
				else:
					if cfg.debug:
						traceback.print_exc()
					raise InvalidOUID(f"Error fetching OUID: {response.status} - {response.reason}")