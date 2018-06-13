output "cw_cron_event_id" {
  value = "${aws_cloudwatch_event_rule.cron.id}"
}

output "cw_cron_alarm_id" {
  value = "${aws_cloudwatch_metric_alarm.cron.id}"
}

output "lambda_id" {
  value = "${aws_lambda_function.iam_lambda.id}"
}

output "lambda_arn" {
  value = "${aws_lambda_function.iam_lambda.arn}"
}
