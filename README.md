
# Currency Monitoring

## Overview
This project involves developing a bot using Python to monitor currency exchange rates via the Uphold API. The bot checks rates at regular intervals, compares them with previously fetched rates, and logs an alert if a specified percentage change is detected. Asynchronous programming is utilized for efficiency and scalability.

## Project Components
1. Configuration and Environment Setup
    - Files:
      - config.py y_config.yaml
      - .env
    - Description:
      - Configuration Loading:
         - `load_config(file_path)`: Reads settings from currency_config.yaml 
      - Environment Variables:

2. API Uphold
    - Files:
      - api_uphold.py
    - Description:
      - APIClient Class:
         - Utilizes aiohttp for asynchronous HTTP requests to the Uphold API.
         - Example: Fetches the BTC-USD rate from https://api.uphold.com/v0/ticker/BTC-USD.
         - Handles rate limiting by checking the HTTP response status. If status is 429 (Too Many Requests), it retries after the specified interval.

3. Currency Monitor
    - Files:
      - monitor.py
    - Description:
      - CurrencyMonitor Class: 
         - Manages monitoring of multiple currency pairs.
         - Example: Monitors pairs like BTC-USD and ETH-USD concurrently.
         - Fetches current rates and compares them with the last recorded rates from DynamoDB. Logs an alert if the rate changes by the specified threshold (e.g., 0.01%).

4. DynamoDB Client
    - Files:
      - dynamodb_client.py
    - Description:
      - DynamoDBClient Class:
         - Interacts with DynamoDB to store and retrieve currency rates and configuration information.
         - Example:
            - `get_last_alert`
            - `post_alert`

5. Main Execution Script
    - Files:
      - main.py
    - Description:
      - Main Function:
         - Sets up logging and loads configuration.
         - Initializes CurrencyMonitor with parameters from currency_config.yaml.
         - Example: Starts monitoring process for pairs like BTC-USD, ETH-USD at intervals specified in the configuration.
         - Ensures DynamoDB tables are created using `create_table()` before starting the monitoring.

## Asynchronous Programming
- Reason for Asynchronous Programming:
  - Efficiency: Allows handling multiple tasks simultaneously, crucial for IO-bound tasks like network requests.
  - Scalability: Manages concurrent HTTP requests for multiple currency pairs effectively.
  - Responsiveness: Keeps the bot responsive, handling retries and rate limits smoothly.
- Libraries Used:
  - aiohttp: For non-blocking HTTP requests to the Uphold API.
  - asyncio: For managing asynchronous tasks and concurrency.
  - aiobotocore: For asynchronous interactions with DynamoDB.



The following commands can be used to print the current DynamoDB table in different formats:

- Credentials:
```
export REGION_NAME='us-west-2'
export AWS_ACCESS_KEY_ID='fakeAccessKeyId'
export AWS_SECRET_ACCESS_KEY='fakeSecretAccessKey'
```

1. Print as JSON:
```
$ aws dynamodb scan --table-name CurrencyAlerts --endpoint-url http://localhost:8000 --output json
```

2. Print as formatted table:
```
$ aws dynamodb scan --table-name CurrencyAlerts --endpoint-url http://localhost:8000 --output json \
| jq -r '.Items[] | [.pair.S, .rate.N, (.timestamp.N | tonumber | strftime("%Y-%m-%d %H:%M:%S")), .change_threshold.N, .check_interval.N] | @tsv' \
| column -t

```

3. Print as CSV:
```
$ aws dynamodb scan --table-name CurrencyAlerts --endpoint-url http://localhost:8000 --output json \
| jq -r '["pair", "rate", "timestamp", "change_threshold", "check_interval"], (.Items[] | [.pair.S, .rate.N, (.timestamp.N | tonumber | strftime("%Y-%m-%d %H:%M:%S")), .change_threshold.N, .check_interval.N]) | @csv'

```
