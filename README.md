## AWS IAM access key manager
[![pipeline status](https://gitlab.com/christianTragesser/aws-access-key-manager/badges/master/pipeline.svg)](https://gitlab.com/christianTragesser/aws-access-key-manager/commits/master)

A boto3 utility used for automated evaluation, invalidation, and renewal of IAM user access keys.  Keys older than the expire threshold are inactivated; keys older than the warn threshold but less than expire produce warnings with time-to-live values.  Warning, expiration, and renewal notifications are communicated via [Slack webhook](https://api.slack.com/incoming-webhooks) and CloudWatch logs.

#### Dependencies
 * [Slack webhook](https://api.slack.com/incoming-webhooks) for receiving event notifications
 * Expiration policy for IAM Access Keys based on age(default: 90 days)
 * [Terraform](https://www.terraform.io/)

### Install
#### Lambda Terraform module:
1. Clone this repository, then from repository root create the Lambda artifact
```
~/aws-access-key-manager$ bash -C ./build_lambda_bin.sh

 Creating Lambda binary for upload:

Collecting boto3==1.7.36 (from -r requirements.txt (line 1))
.....
.....
-rw-r--r--   1 ctt  ctt   9.5M Jun 13 10:07 key_man.zip

  AWS Lambda bundle key_man.zip created!
```
2. Copy Lambda bundle into a new or existing Terraform configuration directory
```
~$ cp ~/aws-access-key-manager/key_man.zip ~/aws_env/
```
3. Implement the Terraform module in your Terraform configuration providing the desired Slack webhook URL. The Lambda bundle should exist in the same directory as the Terraform configuation containing the module declaration.
```
# main.tf

provider "aws" {
  region = "us-east-1"
}

.....

module "aws_key_man" {
  source = "github.com/christianTragesser/aws-access-key-manager//terraform"

  slack-token = "https://hooks.slack.com/services/<your>/<slack>/<webhook>"
}
```
4. Terraform initialize, plan, and apply for deployment
```
~$ cd ~/aws_env
~/aws_env$ terraform init
  .......
~/aws_env$ terraform plan
  .......
~/aws_env$ terraform apply
  .......
module.aws_key_man.aws_cloudwatch_event_target.cron: Creation complete after 0s (ID: access_key_manager-access_key_manager)
module.aws_key_man.aws_cloudwatch_metric_alarm.cron: Creation complete after 0s (ID: access_key_management)

Apply complete! Resources: 9 added, 0 changed, 0 destroyed.
```

### Customization
The default expiration threshold is 90 days, warnings start at 85 days.  If you'd like to customize these thresholds you can supply `warn-days` and `expire-days` as integer variables when implementing the Terraform module.
```
# main.tf

provider "aws" {
  region = "us-east-1"
}

.....

module "aws_key_man" {
  source = "github.com/christianTragesser/aws-access-key-manager//terraform"

  slack-token = "https://hooks.slack.com/services/<your>/<slack>/<webhook>"
  warn-days = 55
  expire-days = 60
}
```

### Auto-update of IAM user service accounts
When key automation components must reside outside IAM managed infrastructure it is common to create an IAM service account for use with automation tooling. Often a Continuous Integration(CI) server is used to securely store and access IAM secrets pertaining to automation service accounts.  From a security perspective, it is imperative service account keys adhere to the same expiration policy enforced for regular IAM users. Currently this feature allows for automatic renewal of IAM secrets then updating the new secret values in Gitlab CI as group or project level variables; providing seamless management of critical pipeline secrets.

#### Dependencies
 * Gitlab instance URL for [group-level](https://docs.gitlab.com/ee/api/group_level_variables.html#doc-nav) or [project-level](https://docs.gitlab.com/ee/api/project_level_variables.html) variables
 * [Gitlab Personal Token (API)](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#doc-nav)
 * List of desired auto-update IAM user accounts

 To enable the auto-update feature of this module supply `ci-api-url`, `ci-api-token`, and `update-users` as string variables.  The `update-users` variable must be a comma delineated string.
```
# main.tf

provider "aws" {
  region = "us-east-1"
}

.....

module "aws_key_man" {
  source = "github.com/christianTragesser/aws-access-key-manager//terraform"

  slack-token = "https://hooks.slack.com/services/<your>/<slack>/<webhook>"
  ci-api-url = "https://gitlab.com/api/v4/projects/<project id>/variables"
  ci-api-token = "<personal access token>"
  update-users = "ci.user,aws.srv,terraform.svc,bill"
  
}
```
