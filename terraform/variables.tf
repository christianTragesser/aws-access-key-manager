variable "region" {
  type    = string
}

variable "vpc-id" {
  type = string
}

variable "subnet-ids" {
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
