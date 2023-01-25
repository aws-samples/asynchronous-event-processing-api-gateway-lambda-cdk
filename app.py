from infrastructure.main import (
    InfrastructureStack,
)
from aws_cdk import (
    App,
)

app = App()

InfrastructureStack(
    app,
    "AsynchronousEventProcessingAPIGatewayLambda",
    description="Asynchronous Event Processing with API Gateway and Lambda",
)

app.synth()
