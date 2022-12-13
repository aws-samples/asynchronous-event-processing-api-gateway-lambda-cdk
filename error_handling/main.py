from awslambdaric.lambda_context import (
    LambdaContext,
)
from aws_lambda_powertools import (
    Logger,
)
from boto3 import (
    client,
)
from json import (
    dumps,
)
from os import (
    getenv,
)

logger = Logger(
    level=getenv("LOG_LEVEL", "INFO"),
    service="error_handling",
)
TABLE_NAME = getenv("TABLE_NAME")
dynamodb = client("dynamodb")


def handler(event: dict, context: LambdaContext) -> None:
    logger.debug(event)

    id = event["requestPayload"]["id"]
    parameters = event["requestPayload"]["parameters"]

    dynamodb.put_item(
        Item={
            "id": {
                "S": id,
            },
            "parameters": {
                "S": dumps(parameters),
            },
            "status": {
                "S": "Failure",
            },
        },
        TableName=TABLE_NAME,
    )
