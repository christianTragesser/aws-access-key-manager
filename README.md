## AWS IAM access key manager
[![pipeline status](https://gitlab.com/christianTragesser/aws-access-key-manager/badges/master/pipeline.svg)](https://gitlab.com/christianTragesser/aws-access-key-manager/commits/master)

An AWS IAM utility used to evaluate and invalidate (optional) access keys older than a given policy lifetime.  Account IAM users with keys older than the expire or warn thresholds can be reported via [Slack webhook](https://api.slack.com/incoming-webhooks) and container logging.

By default, keys older than 90 days are reported expired.  Keys older than 85 days reporte a warning message with a time-to-live duration.

### Dependencies
* [AWS STS tokens](https://docs.aws.amazon.com/STS/latest/APIReference/welcome.html) paired with an IAM assume role which enables the following access:
  - `iam:GetUser`
  - `iam:ListUsers`
  - `iam:ListAccessKeys`
  - `iam:UpdateAccessKey`
* OCI-compliant container runtime (docker, podman, etc.)

### Use
#### Local Container Image
When running the container image locally, `AWS_REGION` and IAM keys must be set as environment variables for the container runtime.  
```
$ docker run --rm -it -e AWS_REGION="us-east-1" \
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
    registry.gitlab.com/christiantragesser/aws-access-key-manager
```

#### Terraform
The Terraform module included in this repository utilizes AWS Fargate and Cloudwatch Events to evaluate keys at a desired interval.  AWS Region, VPC ID, and subnet IDs are required variables for the Terraform module.
```
# main.tf

module "aws_key_man" {
  source = "github.com/christianTragesser/aws-access-key-manager//terraform"

  region     = "us-east-1"
  vpc_id     = "vpc-0123456789abcde" 
  subnet_ids = ["subnet-0123456789abcde"]
  slack-url  = "https://hooks.slack.com/services/<your>/<slack>/<webhook>"
}
```