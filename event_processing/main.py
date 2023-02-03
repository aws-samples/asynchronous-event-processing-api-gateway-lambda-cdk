from aws_lambda_powertools import (
    Logger,
)
from aws_lambda_powertools.utilities.parser import (
    BaseModel,
    event_parser,
)
from aws_lambda_powertools.utilities.typing import (
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


class Parameters(BaseModel):
    seconds: int


class Event(BaseModel):
    id: str
    parameters: Parameters


TABLE_NAME = getenv("TABLE_NAME")
TIMEOUT = int(getenv("TIMEOUT"))
dynamodb = client("dynamodb")
logger = Logger(
    level=getenv("LOG_LEVEL", "INFO"),
    service="event_processing",
)


def event_processing(parameters: Parameters) -> str:
    seconds = parameters.seconds
    message = f"I slept for {seconds} seconds"

    if seconds > TIMEOUT:
        raise ValueError(f"{seconds} major then {TIMEOUT}")

    sleep(seconds)

    return f"{{\"message\": \"{message}\"}}"


@event_parser(model=Event)
def handler(event: Event, context: LambdaContext) -> None:
    logger.debug(event)

    id = event.id
    parameters = event.parameters
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
