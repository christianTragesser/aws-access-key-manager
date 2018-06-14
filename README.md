## AWS IAM access key manager
A boto3 utility used for automated evaluation, invalidation, and renewal(eventually) of IAM user access keys.  Keys older than the expire threshold are inactivated; keys older than the warn threshold but less than expire produce warnings with time-to-live values.  Warning and expiration notifications are communicated via [Slack webhook](https://api.slack.com/incoming-webhooks) and system logs.

### Quick install
#### Terraform module(Lambda):
1. Clone this repository, from repository root create the Lambda artifact
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
3. Implement the Terraform module in your Terraform configuration providing the desired Slack webhook URL, threshold for warning age, and threshold for expiration age.
```
# main.tf

provider "aws" {
  region = "us-east-1"
}

.....

module "aws_key_man" {
  source = "github.com/christianTragesser/aws-access-key-manager//terraform"
  slack-token = "https://hooks.slack.com/services/<your>/<slack>/<webhook>"
  warn-days = 85
  expire-days = 90
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
~/aws_env$
```
