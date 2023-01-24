from projen import (
    ProjectType,
)
from projen.awscdk import (
    AwsCdkPythonApp,
)

__version__ = "1.0.3"
project = AwsCdkPythonApp(
    auto_merge=False,
    author_email="meronian@amazon.ch",
    author_name="Andrea Meroni",
    cdk_version="2.61.0",
    commit_generated=False,
    description="Asynchronous Processing with API Gateway and Lambda",
    dev_deps=[
        "autopep8==2.0.1",
        "aws-lambda-powertools==2.6.0",
        "bandit==1.7.4",
        "botocore==1.29.53",
        "boto3==1.26.53",
        "cfn-lint==0.72.9",
        "checkov==2.2.281",
        "commitizen==2.39.1",
        "pre-commit==2.21.0",
        "pydantic==1.10.4",
        "pytest-env==0.8.1",
        "pytest==7.2.1",
    ],
    github=False,
    license="MIT-0",
    module_name="infrastructure",
    name="asynchronous-processing-api-gateway-lambda-cdk",
    project_type=ProjectType.APP,
    version=__version__,
)

project.add_git_ignore(".nvmrc")

autopep8 = project.add_task(
    description="Lints using autopep8",
    exec="autopep8 .",
    name="autopep8",
)
bandit = project.add_task(
    description="Scans using bandit",
    exec="bandit --configfile pyproject.toml --recursive .",
    name="bandit",
)
bootstrap = project.add_task(
    description="Bootstraps CDK",
    exec="cdk bootstrap",
    name="bootstrap",
)
bump = project.add_task(
    description="Bumps version",
    exec=f"cz bump --check-consistency {__version__}",
    name="bump",
)
cfn_lint = project.add_task(
    description="Lints using cfn-lint",
    exec="cfn-lint cdk.out/*.template.json",
    name="cfn-lint",
)
checkov = project.add_task(
    description="Scans using checkov",
    exec="checkov --config-file .checkov.yaml --directory .",
    name="checkov",
)
lint = project.add_task(
    description="Lints code",
    name="lint",
)
release = project.add_task(
    description="Releases version",
    name="release",
)
scan = project.add_task(
    description="Scans code",
    name="scan",
)

lint.spawn(autopep8)
lint.spawn(cfn_lint)
release.spawn(project.tasks.try_find("build"))
release.spawn(lint)
release.spawn(scan)
release.spawn(bump)
scan.spawn(bandit)
scan.spawn(checkov)
project.synth()
