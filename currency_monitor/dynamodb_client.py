import boto3
import aiobotocore.session
import time
import logging
import os

from config import load_config

DYNAMO_ENDPOINT = os.environ.get('DYNAMO_ENDPOINT')
REGION_NAME = os.environ.get('REGION_NAME')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

logger = logging.getLogger(__name__)

def create_table(n_pairs: int):
    try:
        client = boto3.client(
            'dynamodb',
            endpoint_url=DYNAMO_ENDPOINT,
            region_name=REGION_NAME,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

        client.create_table(
            TableName='CurrencyAlerts',
            KeySchema=[
                {'AttributeName': 'pair', 'KeyType': 'HASH'},
                {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'pair', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'N'},
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': n_pairs,
                'WriteCapacityUnits': n_pairs
            }
        )

        waiter = client.get_waiter('table_exists')
        waiter.wait(TableName='CurrencyAlerts')
        logger.info("Table 'CurrencyAlerts' created successfully.")

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")


class DynamoDB:
    """
    A class representing a DynamoDB client.

    This class provides methods to interact with DynamoDB using the aiobotocore library.

    Attributes:
        session (aiobotocore.session.AioSession): The session object for the client.
        endpoint_url (str): The endpoint URL for the DynamoDB service.
        region_name (str): The AWS region name.
        aws_access_key_id (str): The AWS access key ID.
        aws_secret_access_key (str): The AWS secret access key.

    """
    def __init__(self):
        """
        Initializes a new instance of the DynamoDBClient class.

        The session object is created using aiobotocore's get_session() method.
        The endpoint URL, region name, AWS access key ID, and AWS secret access key are set to their respective values.
        The client object is initially set to None.

        """
        self.session = aiobotocore.session.get_session()
        self.endpoint_url = DYNAMO_ENDPOINT
        self.region_name = REGION_NAME
        self.aws_access_key_id = AWS_ACCESS_KEY_ID
        self.aws_secret_access_key = AWS_SECRET_ACCESS_KEY
        self.config = load_config('currency_config.yaml')

    async def get_client(self):
        """
        Creates and returns a DynamoDB client.

        Returns:
            DynamoDBClient: The DynamoDB client.

        Raises:
            None.
        """
        return self.session.create_client(
            'dynamodb',
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    async def get_last_alert(self, pair: str) -> float | None:
        """
        Retrieves the last alert rate for a given currency pair from DynamoDB.

        Args:
            pair (str): The currency pair to retrieve the last alert rate for.

        Returns:
            float or None: The last alert rate as a float if it exists, None otherwise.
        """
        async with await self.get_client() as client:
            try:
                response = await client.query(
                    TableName='CurrencyAlerts',
                    KeyConditionExpression='pair = :pair',
                    ExpressionAttributeValues={
                        ':pair': {'S': pair}
                    },
                    ScanIndexForward=False,
                    Limit=1
                )
                if 'Items' in response and len(response['Items']) > 0:
                    return float(response['Items'][0]['rate']['N'])
                return None
            except Exception as e:
                logger.error(f"Error getting last rate from DynamoDB: {e}")
                return None

    async def post_alert(self, pair: str, rate: float) -> None:
        """
        Posts an alert to the DynamoDB table 'CurrencyAlerts'.

        Args:
            pair (str): The currency pair for the alert.
            rate (float): The rate for the alert.

        Raises:
            Exception: If there is an error updating the rate in DynamoDB.

        """
        async with await self.get_client() as client:
            try:
                timestamp = int(time.time())
                await client.put_item(
                    TableName='CurrencyAlerts',
                    Item={
                        'pair': {'S': pair},
                        'rate': {'N': str(rate)},
                        'timestamp': {'N': str(timestamp)},
                        'change_threshold': {'N': str(self.config['change_threshold'])},
                        'check_interval': {'N': str(self.config['check_interval'])}
                    }
                )
            except Exception as e:
                logger.error(f"Error updating rate in DynamoDB: {e}")
