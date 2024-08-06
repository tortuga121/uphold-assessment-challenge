import asyncio
import logging
import aiohttp
from dynamodb_client import DynamoDB
from api_client import UpholdAPI

logger = logging.getLogger(__name__)


class CurrencyMonitor:
    """
    A class that monitors currency rates and posts alerts based on rate changes.

    Args:
        check_interval (float): The interval (in seconds) between rate checks.
        change_threshold (float): The minimum rate change percentage to trigger an alert.

    Attributes:
        dynamodb_client (DynamoDB): An instance of the DynamoDB client.
        api_client (UpholdAPI): An instance of the UpholdAPI client.
        check_interval (float): The interval (in seconds) between rate checks.
        change_threshold (float): The minimum rate change percentage to trigger an alert.
    """

    def __init__(self, check_interval, change_threshold):
        """
        Initializes a new instance of the CurrencyMonitor class.

        Args:
            check_interval (float): The interval (in seconds) between rate checks.
            change_threshold (float): The minimum rate change percentage to trigger an alert.

        """
        self.dynamodb_client = DynamoDB()
        self.api_client = UpholdAPI()
        self.check_interval = check_interval
        self.change_threshold = change_threshold

    async def monitor_pair(self, session, pair):
        """
        Monitors the rate of a currency pair and posts alerts if the rate changes significantly.

        Args:
            session (aiohttp.ClientSession): The aiohttp client session.
            pair (str): The currency pair to monitor.

        """
        while True:
            try:
                current_rate = await self.api_client.fetch_rate(session, pair)
                if current_rate is None:
                    await asyncio.sleep(0.5)
                    continue

                last_rate = await self.dynamodb_client.get_last_alert(pair)
                if last_rate is not None:
                    change_percentage = abs((current_rate - last_rate) / last_rate)
                    if change_percentage >= self.change_threshold:
                        logger.info(f"Alert! {pair} rate changed by {change_percentage:.6f}%")

                await self.dynamodb_client.post_alert(pair, current_rate)
            except Exception as e:
                logger.error(f"Error monitoring pair {pair}: {e}")

            await asyncio.sleep(self.check_interval)

    async def run(self, pairs):
        """
        Runs the currency monitoring for multiple currency pairs.

        Args:
            pairs (list): A list of currency pairs to monitor.

        """
        async with aiohttp.ClientSession() as session:
            tasks = [self.monitor_pair(session, pair) for pair in pairs]
            await asyncio.gather(*tasks)
