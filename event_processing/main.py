from aws_lambda_powertools import (
    Logger,
)
from awslambdaric.lambda_context import (
    LambdaContext,
)
from boto3 import (
    client,
)
from os import (
    getenv,
)
from time import (
    sleep,
)

logger = Logger(
    level=getenv("LOG_LEVEL", "INFO"),
    service="jobs_processing",
)
TABLE_NAME = getenv("TABLE_NAME")
TIMEOUT = int(getenv("TIMEOUT"))
dynamodb = client("dynamodb")


def event_processing(parameters: dict) -> str:
    seconds = parameters["seconds"]
    message = f"I slept for {seconds} seconds"

    if seconds > TIMEOUT:
        raise ValueError(f"{seconds} major then {TIMEOUT}")

    sleep(seconds)

    return f"{{\"message\": \"{message}\"}}"


def handler(event: dict, context: LambdaContext) -> None:
    logger.debug(event)

    id = event["id"]
    parameters = event["parameters"]
    results = event_processing(parameters)

    dynamodb.put_item(
        Item={
            "id": {
                "S": id,
            },
            "results": {
                "S": results,
            },
            "status": {
                "S": "Success",
            },
        },
        TableName=TABLE_NAME,
    )
