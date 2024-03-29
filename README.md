## AWS IAM access key manager
[![pipeline status](https://gitlab.com/christianTragesser/aws-access-key-manager/badges/master/pipeline.svg)](https://gitlab.com/christianTragesser/aws-access-key-manager/commits/master)

An AWS IAM utility used to evaluate and invalidate access keys older than a given policy lifetime.  Account IAM users with keys older than the expire or warn thresholds can be reported via [Slack webhook](https://api.slack.com/incoming-webhooks) and application logs.


### Dependencies
AWS user credentials with the following IAM access:
  - `iam:GetUser`
  - `iam:ListUsers`
  - `iam:ListAccessKeys`
  - `iam:UpdateAccessKey`

### Configuration
#### AWS Credentials
AWS security credentials are configured by either environment variables (precedence) or `default` profile in `$HOME/.aws/credentials`.  
The following information must be set as environment variables if not provide by a credentials file:
  - `AWS_REGION`
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_SESSION_TOKEN` (STS session)

#### Warning and Expiration Threasholds
By default, keys older than 90 days are reported expired.  
Keys older than 85 days report a warning message with a time-to-live duration.  
These thresholds can be customized by setting `WARN_DAYS` and `EXPIRE_DAYS` environment variables.
```
export WARN_DAYS=12
export EXPIRE_DAYS=14
```

#### Slack Reports
Reports can be sent to a Slack channel with the `SLACK_URL` environment variable and [Webhook URL](https://api.slack.com/messaging/webhooks).
```
export SLACK_URL="https://hooks.slack.com/services/<your>/<slack>/<webhook>"
```
 
 #### Disable Expired Keys
 By default expired keys are only reported.  
 To automatically inactivate expired keys set the `KEY_DISABLE` environment variable to `True`. 
```
export KEY_DISABLE="True"
```

### Use
`aws-access-key-manager` can be run as a binary package or container image.
#### Binary Package (AMD64)
The `aws-access-key-manager` [binary package](https://github.com/christianTragesser/aws-access-key-manager/releases) is available for the following platforms:
* Linux
* MacOS
* Windows

#### Container Image
```
$ docker run --rm -it \
    -e AWS_REGION=$AWS_REGION \
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
    registry.gitlab.com/christiantragesser/aws-access-key-manager
```

#### Terraform
This repository includes a Terraform module which utilizes AWS Fargate and Cloudwatch Events.  
AWS `region`, `vpc-id`, and `subnet-ids` are required variables.
```
module "aws_key_man" {
  source = "github.com/christianTragesser/aws-access-key-manager//terraform"

  region      = "us-east-1"
  vpc-id      = "vpc-0123456789abcde" 
  subnet-ids  = ["subnet-0123456789abcdef", "subnet-abcdef0123456789"]
  slack-url   = "https://hooks.slack.com/services/<your>/<slack>/<webhook>"
  key-disable = "True"
}
```