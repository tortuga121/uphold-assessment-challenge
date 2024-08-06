import os
import yaml

API_BASE_URL = 'https://api.uphold.com/v0/ticker/'

DYNAMO_ENDPOINT = os.getenv('DYNAMO_ENDPOINT', 'http://localhost:8000')


def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)
