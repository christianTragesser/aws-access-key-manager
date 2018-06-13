# Module creates Cloudwatch(CW) cron event rule, CW cron alarm, CW logging,
# Lambda for accessKeyManager, and least privilege IAM roles/policies

# Cloudwatch resources
resource "aws_cloudwatch_event_rule" "cron" {
  name                = "${var.cw-rule}"
  description         = "Audit access key age"
  schedule_expression = "cron(${var.cron-schedule})"
}

resource "aws_cloudwatch_event_target" "cron" {
  target_id = "${var.cw-rule}"
  rule      = "${aws_cloudwatch_event_rule.cron.name}"
  arn       = "${aws_lambda_function.iam_lambda.arn}"
}

resource "aws_cloudwatch_metric_alarm" "cron" {
  alarm_name          = "access_key_management"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "60"
  statistic           = "Maximum"
  threshold           = "1"
  alarm_description   = "This metric monitors for lambda errors"
  treat_missing_data  = "notBreaching"

  insufficient_data_actions = []

  dimensions {
    FunctionName = "${aws_lambda_function.iam_lambda.id}"
  }
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.iam_lambda.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.cron.arn}"
}

resource "aws_iam_role_policy" "lamba_logs" {
  name = "logging_for_lambda"
  role = "${aws_iam_role.lambda_iam.id}"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

# Lambda resources
resource "aws_lambda_alias" "lambda_alias" {
  name             = "access_key_management"
  description      = "Manage IAM user access keys"
  function_name    = "${aws_lambda_function.iam_lambda.function_name}"
  function_version = "$LATEST"
}

resource "aws_iam_role_policy" "management_policy" {
  name = "access_key_management"
  role = "${aws_iam_role.lambda_iam.id}"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:UpdateAccessKey",
        "iam:ListUsers",
        "iam:GetUser",
        "iam:ListAccessKeys",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role" "lambda_iam" {
  name        = "access_key_management"
  description = "IAM access key auditor"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_lambda_function" "iam_lambda" {
  filename         = "${var.lambda-zip}"
  function_name    = "access_key_management"
  role             = "${aws_iam_role.lambda_iam.arn}"
  handler          = "accessKeyManager.handler"
  source_code_hash = "${base64sha256(file("${var.lambda-zip}"))}"
  runtime          = "python2.7"
  timeout          = 5

  environment {
    variables = {
      SLACK_URL   = "${var.slack-token}"
      WARN_DAYS   = "${var.warn-days}"
      EXPIRE_DAYS = "${var.expire-days}"
    }
  }
}
