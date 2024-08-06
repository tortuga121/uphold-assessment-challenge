import asyncio
import logging
import yaml
from monitor import CurrencyMonitor
from dynamodb_client import create_table
from config import load_config
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


load_dotenv()


def main():
    monitor = CurrencyMonitor(check_interval, change_threshold)
    asyncio.run(monitor.run(pairs))


if __name__ == "__main__":
    config = load_config('currency_config.yaml')
    change_threshold = config['change_threshold']
    check_interval = config['check_interval']
    pairs = config['pairs']
    create_table(len(pairs))
    main()
