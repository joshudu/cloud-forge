import boto3
import json
import os
from functools import lru_cache
from typing import Optional

def get_secret(secret_name: str) -> dict:
    """
    Fetch a secret from AWS Secrets Manager.
    Falls back to environment variables for local development.
    """
    # Local development fallback
    if os.getenv("ENVIRONMENT") == "local":
        return {}

    client = boto3.client(
        "secretsmanager",
        region_name=os.getenv("AWS_REGION", "eu-west-1")
    )

    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])

@lru_cache(maxsize=None)
def get_db_secret() -> dict:
    return get_secret("cloudforge/staging/db")

@lru_cache(maxsize=None)
def get_jwt_secret() -> dict:
    return get_secret("cloudforge/staging/jwt")