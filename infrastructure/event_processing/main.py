from aws_cdk import (
    BundlingOptions,
    Duration,
    RemovalPolicy,
)
from aws_cdk.aws_dynamodb import (
    Attribute,
    AttributeType,
    Table,
    TableEncryption,
)
from aws_cdk.aws_events import (
    EventBus,
    EventPattern,
)
from aws_cdk.aws_kms import (
    Key,
)
from aws_cdk.aws_lambda import (
    Code,
    Function,
    LayerVersion,
    Runtime,
)
from aws_cdk.aws_lambda_destinations import (
    EventBridgeDestination,
    LambdaDestination,
)
from constructs import (
    Construct,
)
from pathlib import (
    Path,
)


class EventProcessingConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        error_handling_timeout: int = 5,
        event_processing_timeout: int = 300,
        max_event_age: int = 21600,
        pending_window: int = 7,
        read_capacity: int = 5,
        removal_policy: RemovalPolicy = RemovalPolicy.DESTROY,
        reserved_concurrent_executions: int = 100,
        retry_attempts: int = 0,
        write_capacity: int = 5,
    ) -> None:
        super().__init__(
            scope,
            construct_id,
        )

        self.__failed_jobs_event_bus = EventBus(
            self,
            "FailedJobsEventBus",
        )
        self.__jobs_table_key = Key(
            self,
            "JobsTableKey",
            alias="alias/JobsTableKey",
            enable_key_rotation=True,
            pending_window=Duration.days(pending_window),
            removal_policy=removal_policy,
        )
        self.__powertools_layer = LayerVersion(
            self,
            "PowertoolsLayer",
            code=Code.from_asset(
                str(
                    Path(__file__).
                    parent.
                    parent.
                    parent.
                    joinpath("powertools").
                    resolve()
                ),
                bundling=BundlingOptions(
                    command=[
                        "bash",
                        "-c",
                        ("mkdir /asset-output/python && "
                         "pip install "
                         "--requirement /asset-input/requirements.txt "
                         "--target /asset-output/python"),
                    ],
                    image=Runtime.PYTHON_3_9.bundling_image,
                ),
            ),
            compatible_runtimes=[
                Runtime.PYTHON_3_9,
            ],
            description="AWS Lambda Powertools for Python",
            license="MIT-0",
        )
        self.jobs_table = Table(
            self,
            "JobsTable",
            encryption=TableEncryption.CUSTOMER_MANAGED,
            encryption_key=self.__jobs_table_key,
            partition_key=Attribute(
                name="id",
                type=AttributeType.STRING,
            ),
            point_in_time_recovery=True,
            read_capacity=read_capacity,
            removal_policy=removal_policy,
            write_capacity=write_capacity,
        )
        self.__error_handling_function = Function(
            self,
            "ErrorHandlingFunction",
            code=Code.from_asset(
                str(
                    Path(__file__).
                    parent.
                    parent.
                    parent.
                    joinpath("error_handling").
                    resolve()
                ),
                bundling=BundlingOptions(
                    command=[
                        "bash",
                        "-c",
                        ("cp /asset-input/main.py "
                         "--target /asset-output "
                         "--update"),
                    ],
                    image=Runtime.PYTHON_3_9.bundling_image,
                ),
            ),
            environment={
                "TABLE_NAME": self.jobs_table.table_name,
            },
            handler="main.handler",
            layers=[
                self.__powertools_layer,
            ],
            max_event_age=Duration.seconds(max_event_age),
            on_failure=EventBridgeDestination(self.__failed_jobs_event_bus),
            reserved_concurrent_executions=reserved_concurrent_executions,
            retry_attempts=retry_attempts,
            runtime=Runtime.PYTHON_3_9,
            timeout=Duration.seconds(error_handling_timeout),
        )
        self.event_processing_function = Function(
            self,
            "EventProcessingFunction",
            code=Code.from_asset(
                str(
                    Path(__file__).
                    parent.
                    parent.
                    parent.
                    joinpath("event_processing").
                    resolve()
                ),
                bundling=BundlingOptions(
                    command=[
                        "bash",
                        "-c",
                        ("cp /asset-input/main.py "
                         "--target /asset-output "
                         "--update"),
                    ],
                    image=Runtime.PYTHON_3_9.bundling_image,
                ),
            ),
            environment={
                "TABLE_NAME": self.jobs_table.table_name,
                "TIMEOUT": str(event_processing_timeout),
            },
            handler="main.handler",
            layers=[
                self.__powertools_layer,
            ],
            max_event_age=Duration.seconds(max_event_age),
            on_failure=LambdaDestination(self.__error_handling_function),
            reserved_concurrent_executions=reserved_concurrent_executions,
            retry_attempts=retry_attempts,
            runtime=Runtime.PYTHON_3_9,
            timeout=Duration.seconds(event_processing_timeout),
        )

        self.__error_handling_function.node.default_child.add_metadata(
            "checkov",
            {
                "skip": [
                    {
                        "comment": ("This function uses "
                                    "Lambda Destinations"),
                        "id": "CKV_AWS_116",
                    },
                    {
                        "comment": ("This function is not meant "
                                    "to be run inside a VPC"),
                        "id": "CKV_AWS_117",
                    },
                    {
                        "comment": ("A customer managed key "
                                    "is not required"),
                        "id": "CKV_AWS_173",
                    },
                ],
            },
        )
        self.__failed_jobs_event_bus.archive(
            "FailedJobsEventArchive",
            description="Failed Jobs Event Archive",
            event_pattern=EventPattern(),
        )
        self.event_processing_function.node.default_child.add_metadata(
            "checkov",
            {
                "skip": [
                    {
                        "comment": ("This function uses "
                                    "Lambda Destinations"),
                        "id": "CKV_AWS_116",
                    },
                    {
                        "comment": ("This function is not meant "
                                    "to be run inside a VPC"),
                        "id": "CKV_AWS_117",
                    },
                    {
                        "comment": ("A customer managed key "
                                    "is not required"),
                        "id": "CKV_AWS_173",
                    },
                ],
            },
        )
        self.jobs_table.grant_read_write_data(self.__error_handling_function)
        self.jobs_table.grant_read_write_data(self.event_processing_function)
