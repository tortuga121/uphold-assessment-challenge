import logging
import asyncio
from config import API_BASE_URL, load_config
import aiohttp

logger = logging.getLogger(__name__)


class UpholdAPI:
    """
    A class representing an API client for fetching currency rates.

    """
    def __init__(self):
        self.config = load_config('currency_config.yaml')
        self.timeout = aiohttp.ClientTimeout(total=self.config['check_interval'])

    async def fetch_rate(self, session: aiohttp.ClientSession, pair: str):
        """
        Fetches the currency rate for a given pair.

        Args:
            session (aiohttp.ClientSession): The client session for making API requests.
            pair (str): The currency pair to fetch the rate for.

        Returns:
            float: The bid rate for the currency pair.

        Raises:
            Exception: If an error occurs while fetching the rate.

        """
        url = f"{API_BASE_URL}{pair}"
        try:
            async with session.get(url, timeout=self.timeout) as response:
                if response.status == 429:
                    retry_after = response.headers.get('Retry-After', '5')
                    retry_after = int(retry_after)
                    if retry_after >= self.config['check_interval']:
                        return None
                    logger.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
                    await asyncio.sleep(retry_after)
                    return await self.fetch_rate(session, pair)
                response.raise_for_status()
                response_json = await response.json()
                return float(response_json['bid'])
        except Exception as e:
            logger.error(f"Error fetching rate for {pair}: {e}")
            return None
