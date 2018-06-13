variable "cw-rule" {
  default = "access_key_manager"
}

variable "cron-schedule" {
  default = "0 7 ? * * *"
}

variable "lambda-zip" {
  default = "key_man.zip"
}

variable "warn-days" {
  default = 85
}

variable "expire-days" {
  default = 90
}

variable "slack-token" {}
