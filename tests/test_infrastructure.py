from infrastructure.main import (
    InfrastructureStack,
)
from aws_cdk import (
    App,
)
from aws_cdk.assertions import (
    Match,
    Template,
)
from pytest import (
    fixture,
)


@fixture
def template() -> Template:
    app = App()
    stack = InfrastructureStack(
        app,
        "AsynchronousEventProcessingAPIGatewayLambda",
        description="Asynchronous Event Processing with API Gateway and Lambda"
    )
    template = Template.from_stack(stack)

    yield template


def test_jobs_api_is_setup(template: Template) -> None:
    template.has_resource("AWS::ApiGateway::Method", {
        "Properties": {
            "AuthorizationType": "AWS_IAM",
            "HttpMethod": "GET",
        },
    })
    template.has_resource("AWS::ApiGateway::Method", {
        "Properties": {
            "AuthorizationType": "AWS_IAM",
            "HttpMethod": "POST",
        },
    })
    template.has_resource("AWS::ApiGateway::Resource", {
        "Properties": {
            "PathPart": "{jobId}",
        },
    })
    template.has_resource("AWS::ApiGateway::Resource", {
        "Properties": {
            "PathPart": "jobs",
        },
    })
    template.has_resource("AWS::ApiGateway::Stage", {
        "Properties": {
            "StageName": "dev",
        },
    })
    template.has_resource("AWS::IAM::Policy", {
        "Properties": {
            "PolicyDocument": {
                "Statement": Match.array_with([
                    Match.object_like({
                        "Action": "execute-api:Invoke",
                    }),
                ]),
            },
        },
    })
    template.has_resource("AWS::IAM::Role", {
        "Properties": {
            "AssumeRolePolicyDocument": {
                "Statement": [{
                    "Action": "sts:AssumeRole",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": Match.object_like({
                            "Fn::Join": [
                                "",
                                Match.array_with([
                                    ":root",
                                ]),
                            ],
                        }),
                    },
                }],
            },
        },
    })
    template.has_resource("AWS::IAM::Role", {
        "Properties": {
            "AssumeRolePolicyDocument": {
                "Statement": [{
                    "Action": "sts:AssumeRole",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "apigateway.amazonaws.com",
                    },
                }],
            },
            "ManagedPolicyArns": Match.absent(),
        }
    })
    template.has_resource("AWS::IAM::Role", {
        "Properties": {
            "AssumeRolePolicyDocument": {
                "Statement": [{
                    "Action": "sts:AssumeRole",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "apigateway.amazonaws.com",
                    },
                }],
            },
            "ManagedPolicyArns": [{
                "Fn::Join": [
                    "",
                    Match.array_with([
                        "/".join([
                            ":iam::aws:policy",
                            "service-role",
                            "AmazonAPIGatewayPushToCloudWatchLogs",
                        ]),
                    ]),
                ],
            }],
        },
    })
    template.has_resource("AWS::KMS::Alias", {
        "Properties": {
            "AliasName": "alias/JobsAPIAccessLogsKey",
        }
    })
    template.has_resource("AWS::Logs::LogGroup", {
        "Properties": {
            "LogGroupName": "/aws/apigateway/JobsAPIAccessLogs",
            "RetentionInDays": 30,
        }
    })
    template.resource_count_is("AWS::ApiGateway::Account", 1)


def test_jobs_functions_are_setup(template: Template) -> None:
    template.has_resource("AWS::Events::Archive", {
        "Properties": {
            "RetentionDays": 0,
        },
    })
    template.has_resource("AWS::Lambda::Function", {
        "Properties": {
            "Timeout": 300,
        },
    })
    template.has_resource("AWS::Lambda::Function", {
        "Properties": {
            "Timeout": 5,
        },
    })
    template.resource_count_is("AWS::Events::EventBus", 1)
    template.resource_count_is("AWS::Lambda::EventInvokeConfig", 2)


def test_jobs_table_is_setup(template: Template) -> None:
    template.has_resource("AWS::DynamoDB::Table", {
        "DeletionPolicy": "Delete",
        "UpdateReplacePolicy": "Delete",
    })
    template.has_resource("AWS::KMS::Alias", {
        "Properties": {
            "AliasName": "alias/JobsTableKey",
        }
    })
    template.has_resource("AWS::KMS::Key", {
        "DeletionPolicy": "Delete",
        "Properties": {
            "PendingWindowInDays": 7,
        },
        "UpdateReplacePolicy": "Delete",
    })
