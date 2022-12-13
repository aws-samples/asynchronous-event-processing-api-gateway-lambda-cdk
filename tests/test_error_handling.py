from awslambdaric.lambda_context import (
    LambdaContext,
)
from botocore.stub import (
    Stubber,
)
from error_handling.main import (
    dynamodb,
    handler,
)
from json import (
    dumps,
)
from pytest import (
    fixture,
)
from tests.fixtures import (
    context,
)


@fixture
def dynamodb_stub(event: dict) -> Stubber:
    dynamodb_stub = Stubber(dynamodb)
    parameters = event["requestPayload"]["parameters"]

    dynamodb_stub.add_response(
        "put_item",
        expected_params={
            "Item": {
                "id": {
                    "S": "1",
                },
                "parameters": {
                    "S": dumps(parameters),
                },
                "status": {
                    "S": "Failure",
                },
            },
            "TableName": "jobs",
        },
        service_response=dict(),
    )

    yield dynamodb_stub


@fixture
def event() -> dict:
    event = {
        "requestPayload": {
            "id": "1",
            "parameters": {
                "seconds": 301,
            },
        },
    }

    yield event


def test_error_handling(
    context: LambdaContext,
    dynamodb_stub: Stubber,
    event: dict,
) -> None:
    with dynamodb_stub:
        handler(event, context)
