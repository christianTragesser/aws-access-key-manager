# Module creates Cloudwatch(CW) cron event rule, CW cron alarm, CW logging,
# Lambda for accessKeyManager, and least privilege IAM roles/policies

locals {
  keyman_id = "keyman"
  keyman_tags = {
    "Name" : "keyman"
    "created-by" : "terraform/aws-access-key-management"
  }
}

data "aws_caller_identity" "keyman" {}