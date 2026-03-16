import boto3
import json
import os
from app.core.logging import get_logger

logger = get_logger(__name__)

def get_sqs_client():
    return boto3.client(
        "sqs",
        region_name=os.getenv("AWS_REGION", "eu-west-1")
    )

async def publish_event(event_type: str, payload: dict) -> bool:
    """
    Publish an event to SQS.
    Returns True if successful, False if failed.
    Failed events will be retried by SQS up to 3 times
    before moving to the dead letter queue.
    """
    queue_url = os.getenv("SQS_QUEUE_URL")
    if not queue_url:
        logger.warning("SQS_QUEUE_URL not set — skipping event publish")
        return False

    try:
        client = get_sqs_client()
        message = {
            "event_type": event_type,
            "payload": payload,
        }
        client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message),
            MessageAttributes={
                "event_type": {
                    "DataType": "String",
                    "StringValue": event_type
                }
            }
        )
        logger.info(f"event published", extra={"event_type": event_type})
        return True
    except Exception as e:
        logger.error(f"failed to publish event: {str(e)}", extra={"event_type": event_type})
        return False