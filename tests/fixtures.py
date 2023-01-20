from aws_lambda_powertools.utilities.typing import (
    LambdaContext,
)
from pytest import (
    fixture,
)


@fixture(scope="module")
def context() -> LambdaContext:
    context = LambdaContext()

    yield context
