resource "aws_security_group" "keyman_sg" {
  name        = join("-", [local.keyman_id, "sg"])
  description = "keyman sg"
  vpc_id = var.vpc-id

  tags = local.keyman_tags
}

resource "aws_security_group_rule" "keyman_egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.keyman_sg.id
}

resource "aws_ecs_cluster" "keyman" {
  name = join("-", [local.keyman_id, "cluster"])

  capacity_providers = ["FARGATE"]

  tags = local.keyman_tags
}

resource "aws_ecs_task_definition" "keyman_task" {
  family                   = "access-key-manager"
  task_role_arn            = aws_iam_role.keyman_role.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]

  execution_role_arn = aws_iam_role.keyman_role.arn

  cpu    = 256
  memory = 512
  container_definitions = jsonencode([
    {
      name  = "access-key-manager"
      image = "${var.container-image}:latest"
      environment = [
        { name : "AWS_REGION", value : "${var.region}" },
        { name : "WARN_DAYS", value : "${var.warn-days}" },
        { name : "EXPIRE_DAYS", value : "${var.expire-days}" },
        { name : "SLACK_URL", value : "${var.slack-url}" },
      ]
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.keyman_logs.name
          awslogs-region        = var.region
          awslogs-stream-prefix = "access-key-manager"
        }
      }
    }
  ])

  tags = local.keyman_tags
}