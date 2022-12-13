from infrastructure.main import (
    InfrastructureStack,
)
from aws_cdk import (
    App,
)

app = App()

InfrastructureStack(
    app,
    "AsynchronousProcessingAPIGatewayLambda",
    description="Asynchronous Processing with API Gateway and Lambda",
)

app.synth()
