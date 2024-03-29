from aws_lambda_powertools.utilities.typing import (
    LambdaContext,
)
from botocore.stub import (
    Stubber,
)
from event_processing.main import (
    Event,
    Parameters,
    dynamodb,
    handler,
)
from os import (
    getenv,
)
from pytest import (
    fixture,
)
from tests.fixtures import (
    context,
)


@fixture
def dynamodb_stub(event_success: Event) -> Stubber:
    dynamodb_stub = Stubber(dynamodb)
    parameters = event_success.parameters
    seconds = parameters.seconds
    message = f"I slept for {seconds} seconds"

    dynamodb_stub.add_response(
        "put_item",
        expected_params={
            "Item": {
                "id": {
                    "S": "2",
                },
                "results": {
                    "S": f"{{\"message\": \"{message}\"}}",
                },
                "status": {
                    "S": "Success",
                },
            },
            "TableName": "jobs",
        },
        service_response=dict(),
    )

    yield dynamodb_stub


@fixture
def event_failure() -> Event:
    event_failure = Event(
        id="1",
        parameters=Parameters(
            seconds=301,
        ),
    )

    yield event_failure


@fixture
def event_success() -> Event:
    event_success = Event(
        id="2",
        parameters=Parameters(
            seconds=1,
        ),
    )

    yield event_success


def test_job_processing_failure(
    context: LambdaContext,
    event_failure: Event,
) -> None:
    try:
        parameters = event_failure.parameters
        seconds = parameters.seconds
        timeout = int(getenv("TIMEOUT"))

        handler(event_failure, context)
    except ValueError as value_error:
        error_message = value_error.args[0]

        assert error_message == f"{seconds} major then {timeout}"  # nosec


def test_job_processing_success(
    context: LambdaContext,
    dynamodb_stub: Stubber,
    event_success: Event,
) -> None:
    with dynamodb_stub:
        handler(event_success, context)
