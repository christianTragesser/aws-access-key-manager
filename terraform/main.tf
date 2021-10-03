locals {
  keyman_id = "keyman"
  keyman_tags = {
    "Name" : local.keyman_id
    "created-by" : "terraform/aws-access-key-management"
  }
}

data "aws_caller_identity" "keyman" {}