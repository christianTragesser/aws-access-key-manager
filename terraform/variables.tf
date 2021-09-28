variable "region" {
  type    = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "container-image" {
  type    = string
  default = "registry.gitlab.com/christiantragesser/aws-access-key-manager"
}

variable "warn-days" {
  type    = string
  default = "85"
}

variable "expire-days" {
  type    = string
  default = "90"
}

variable "cron-schedule" {
  type    = string
  default = "0 7 ? * * *"
}

variable "slack-url" {
  type    = string
  default = ""
}

variable "slack-token" {
  type    = string
  default = ""
}

variable "ci-api-url" {
  type    = string
  default = ""
}

variable "ci-api-token" {
  type    = string
  default = ""
}

variable "update-users" {
  type    = string
  default = ""
}
