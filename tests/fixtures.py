from awslambdaric.lambda_context import (
    LambdaContext,
)
from pytest import (
    fixture,
)


@fixture(scope="module")
def context() -> LambdaContext:
    context = LambdaContext(
        cognito_identity={
            "cognitoIdentityId": str(),
        },
        client_context={
            "client": {
                "app_package_name": str(),
                "app_title": str(),
                "app_version_code": str(),
                "app_version_name": str(),
                "installation_id": str(),
            },
            "custom": str(),
            "env": str(),
        },
        epoch_deadline_time_in_ms=str(),
        invoke_id=str(),
    )

    yield context
