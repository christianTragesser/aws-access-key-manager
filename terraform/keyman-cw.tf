# Cloudwatch resources
resource "aws_cloudwatch_log_group" "keyman_logs" {
  name              = "/ecs/keyman-logs-${data.aws_caller_identity.keyman.account_id}"
  retention_in_days = 30

  tags = local.keyman_tags
}

resource "aws_cloudwatch_event_rule" "keyman_cron" {
  name                = join("-", [local.keyman_id, "cron"])
  description         = "Audit access key age"
  schedule_expression = "cron(${var.cron-schedule})"
}

resource "aws_cloudwatch_event_target" "fargate_scheduled_task" {
  rule     = aws_cloudwatch_event_rule.keyman_cron.name
  arn      = aws_ecs_cluster.keyman.arn
  role_arn = aws_iam_role.keyman_role.arn

  ecs_target {
    task_definition_arn = aws_ecs_task_definition.keyman_task.arn
    task_count          = 1
    launch_type         = "FARGATE"
    platform_version    = "1.4.0"

    network_configuration {
      subnets          = var.subnet_ids
      security_groups  = [aws_security_group.keyman_sg.id]
      assign_public_ip = false
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "keyman_cron" {
  alarm_name          = "access_key_management"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/ECS"
  period              = "60"
  statistic           = "Maximum"
  threshold           = "1"
  alarm_description   = "This metric monitors for lambda errors"
  treat_missing_data  = "notBreaching"

  insufficient_data_actions = []

  dimensions = {
    FunctionName = "${aws_ecs_cluster.keyman.arn}"
  }
}