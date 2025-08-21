<p align="center">
  <img src="https://raw.githubusercontent.com/localstack/localstack/main/docs/localstack-readme-banner.svg" alt="LocalStack - A fully functional local cloud stack">
</p>

<p align="center">
  <a href="https://pypi.org/project/localstack-ext/"><img alt="PyPI Version" src="https://img.shields.io/pypi/v/localstack-ext?color=blue"></a>
  <a href="https://hub.docker.com/r/localstack/localstack-pro"><img alt="Docker Pulls" src="https://img.shields.io/docker/pulls/localstack/localstack-pro"></a>
  <a href="https://pypi.org/project/localstack-ext"><img alt="PyPi downloads" src="https://static.pepy.tech/badge/localstack-ext"></a>
  <a href="https://img.shields.io/pypi/l/localstack-ext.svg"><img alt="PyPI License" src="https://img.shields.io/pypi/l/localstack-ext.svg"></a>
  <a href="https://twitter.com/localstack"><img alt="Twitter" src="https://img.shields.io/twitter/url/http/shields.io.svg?style=social"></a>
</p>

# Overview

[LocalStack](https://localstack.cloud) is a cloud service emulator that runs in a single container on your laptop or in your CI environment. With LocalStack, you can run your AWS applications or Lambdas entirely on your local machine without connecting to a remote cloud provider! Whether you are testing complex CDK applications or Terraform configurations, or just beginning to learn about AWS services, LocalStack helps speed up and simplify your testing and development workflow.

LocalStack Pro contains various advanced extensions to the LocalStack base platform, which is [open-source and community driven](https://github.com/localstack/localstack). LocalStack Pro is available as a [Docker image](https://hub.docker.com/r/localstack/localstack-pro). You can read more about it on our documentation for [Docker images](https://docs.localstack.cloud/references/docker-images/#localstack-pro-image).

LocalStack also provides additional features to make your life as a cloud developer easier! Check out LocalStack's [Cloud Developer Tools](https://docs.localstack.cloud/user-guide/tools/) for more information.

## Installation

To install LocalStack Pro, refer to our [installation guide](https://docs.localstack.cloud/getting-started/installation/) and [API Key guide](https://docs.localstack.cloud/getting-started/api-key/).

If you are using the LocalStack Community edition, you can upgrade to LocalStack Pro by pulling the `latest` tag of the LocalStack Pro Docker image. Depending on how you start LocalStack, here’s what you need to look out for:

-   [Docker Compose](https://github.com/localstack/localstack/blob/main/docker-compose-pro.yml): Change the `image` property of your service container from `localstack/localstack`  to  `localstack/localstack-pro`.
-   [LocalStack CLI](https://docs.localstack.cloud/getting-started/installation/#localstack-cli): The quickest way to get started with LocalStack is by using the LocalStack CLI. It allows you to start LocalStack from your command line. Please make sure that you have a working docker environment on your machine before moving on. To use all of LocalStack’s features we recommend to [get a LocalStack account and set up your auth token](https://docs.localstack.cloud/getting-started/auth-token/). The CLI starts and manages the LocalStack docker container.
-   [Docker CLI](https://docs.localstack.cloud/getting-started/api-key/#starting-localstack-via-docker): Similar to when using Docker Compose, you simply need to specify `localstack/localstack-pro` as the image you want to start.

## Usage

LocalStack Pro image includes Pro services and several advanced features. You need to provide an Auth Token to start the LocalStack Pro image successfully. The Auth Token is a personal identifier used for user authentication outside the LocalStack Web Application, particularly in conjunction with the LocalStack core cloud emulator. Its primary functions are to retrieve the user’s license and enable access to advanced features. You can find more information on how to setup an Auth Token on our [Auth Token documentation](https://docs.localstack.cloud/getting-started/auth-token/). You can locate your Auth Token on the [Auth Token page](https://app.localstack.cloud/workspace/auth-token) in the LocalStack Web Application.

To start using LocalStack, check out our documentation at [**docs.localstack.cloud**](https://docs.localstack.cloud).

- [LocalStack Configuration](https://docs.localstack.cloud/references/configuration/)
- [LocalStack in CI](https://docs.localstack.cloud/user-guide/ci/)
- [LocalStack Integrations](https://docs.localstack.cloud/user-guide/integrations/)
- [LocalStack Tools](https://docs.localstack.cloud/user-guide/tools/)
- [Understanding LocalStack](https://docs.localstack.cloud/references/)
- [Troubleshoot](doc/troubleshoot/README.md)

To use LocalStack with a graphical user interface, you can use the following UI clients:

- [LocalStack Web Application](https://app.localstack.cloud/)
- [LocalStack Cockpit](https://localstack.cloud/products/cockpit/)
- [LocalStack Docker Extension](https://docs.localstack.cloud/user-guide/tools/localstack-docker-extension/)

### Docker Compose

You can start LocalStack with [Docker Compose](https://docs.docker.com/compose/) by configuring a `docker-compose.yml` file. Currently, docker-compose version 1.9.0+ is supported.

```
version: "3.8"

services:
  localstack:
    container_name: "${LOCALSTACK_DOCKER_NAME:-localstack-main}"
    image: localstack/localstack-pro
    ports:
      - "127.0.0.1:4566:4566"            # LocalStack Gateway
      - "127.0.0.1:4510-4559:4510-4559"  # external services port range
    environment:
      # LocalStack configuration: https://docs.localstack.cloud/references/configuration/
      - DEBUG=${DEBUG:-0}
    volumes:
      - "${LOCALSTACK_VOLUME_DIR:-./volume}:/var/lib/localstack"
      - "/var/run/docker.sock:/var/run/docker.sock"
```

Start the container by running the following command:

```console
$ docker-compose up
```

Create an ECR registry with LocalStack's [`awslocal`](https://docs.localstack.cloud/user-guide/integrations/aws-cli/#localstack-aws-cli-awslocal) CLI:

```
awslocal ecr create-repository --repository-name test-repository
awslocal ecr describe-repositories --repository-name test-repository
```

**Notes**

- This command pulls the latest image that is built on every commit. Please refer to [Base Image Tags](#base-image-tags) to select the image tag you want to use.

- Mounting the Docker socket `/var/run/docker.sock` as a volume is required for the Lambda service. Check out the [Lambda providers](https://docs.localstack.cloud/user-guide/aws/lambda/) documentation for more information.

Please note that there are a few pitfalls when configuring your stack manually via docker-compose (e.g., required container name, Docker network, volume mounts, and environment variables). We recommend using the LocalStack CLI to validate your configuration, which will print warning messages in case it detects any potential misconfigurations:

```console
$ localstack config validate
```


### Docker CLI

You can directly start the LocalStack container using the Docker CLI. This method requires more manual steps and configuration, but it gives you more control over the container settings.

You can start the Docker container simply by executing the following docker run command:

```console
$ docker run --rm -it -p 4566:4566 -p 4510-4559:4510-4559 localstack/localstack-pro
```

Create a CloudFormation Stack named as `cfn-quickstart-stack.yaml`.

```
{
  "Resources": {
    "LocalBucket": {
      "Type": "AWS::S3::Bucket",
      "Properties": {
        "BucketName": "cfn-quickstart-bucket"
      }
    }
  }
}
```

You can deploy the CloudFormation stack using the [AWS CLI](https://docs.localstack.cloud/user-guide/integrations/aws-cli/#localstack-aws-cli-awslocal) with the [deploy](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/deploy/) command. The deploy command creates and updates CloudFormation stacks. Run the following command to deploy the stack:

```
awslocal cloudformation deploy \
    --stack-name cfn-quickstart-stack \
    --template-file "./cfn-quickstart-stack.yaml"
```

**Notes**

- This command reuses the image if it’s already on your machine, i.e. it will **not** pull the latest image automatically from Docker Hub.

- This command does not bind all ports that are potentially used by LocalStack, nor does it mount any volumes. When using Docker to manually start LocalStack, you will have to configure the container on your own (see [`docker-compose.yml`](https://github.com/localstack/localstack/blob/main/docker-compose.yml) and [Configuration](https://docs.localstack.cloud/references/configuration/)). This could be seen as the “expert mode” of starting LocalStack. If you are looking for a simpler method of starting LocalStack, please use the [LocalStack CLI](https://docs.localstack.cloud/getting-started/installation/#localstack-cli).


## Releases

Please refer to [GitHub releases](https://github.com/localstack/localstack/releases) to see the complete list of changes for each release. For extended release notes, please refer to the [changelog](https://docs.localstack.cloud/references/changelog/).

## Base Image Tags

We do push a set of different image tags for the LocalStack Docker images. When using LocalStack, you can decide which tag you want to use.These tags have different semantics and will be updated on different occasions:

- `latest` (default)
  - This is our default tag.
    It refers to the latest commit which has been fully tested using our extensive integration test suite.
  - This also entails changes that are part of major releases, which means that this tag can contain breaking changes.
  - This tag should be used if you want to stay up-to-date with the latest changes.
- `stable`
  - This tag refers to the latest tagged release.
    It will be updated with every release of LocalStack.
  - This also entails major releases, which means that this tag can contain breaking changes.
  - This tag should be used if you want to stay up-to-date with releases, but don't necessarily need the latest and greatest changes right away.
- `<major>` (e.g. `3`)
  - These tags can be used to refer to the latest release of a specific major release.
    It will be updated with every minor and patch release within this major release.
  - This tag should be used if you want to avoid any potential breaking changes.
- `<major>.<minor>` (e.g. `3.0`)
  - These tags can be used to refer to the latest release of a specific minor release.
    It will be updated with every patch release within this minor release.
  - This tag can be used if you want to avoid any bigger changes, like new features, but still want to update to the latest bugfix release.
- `<major>.<minor>.<patch>` (e.g. `3.0.2`)
  - These tags can be used if you want to use a very specific release.
    It will not be updated.
  - This tag can be used if you really want to avoid any changes to the image (not even minimal bug fixes).

## Where to get help

Get in touch with the LocalStack Team to report 🐞 [issues](https://github.com/localstack/localstack/issues/new/choose), upvote 👍 [feature requests](https://github.com/localstack/localstack/issues?q=is%3Aissue+is%3Aopen+sort%3Areactions-%2B1-desc+), 🙋🏽 ask [support questions](https://docs.localstack.cloud/getting-started/help-and-support/), or 🗣️ discuss local cloud development:

- [LocalStack Slack Community](https://localstack.cloud/contact/)
- [LocalStack GitHub Issue tracker](https://github.com/localstack/localstack/issues)
- [Getting Started - FAQ](https://docs.localstack.cloud/getting-started/faq/)
