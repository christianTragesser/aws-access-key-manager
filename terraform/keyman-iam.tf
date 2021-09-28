resource "aws_iam_role" "keyman_role" {
  name = join("-", [local.keyman_id, "role"])

  assume_role_policy = templatefile("${path.module}/policies/policy-keyman-assume-role.json.tmpl", {})

  tags = local.keyman_tags
}

resource "aws_iam_role_policy" "keyman_policy" {
  name = join("-", [local.keyman_id, "policy"])
  role = aws_iam_role.keyman_role.id

  policy = templatefile("${path.module}/policies/policy-keyman.json.tmpl", {
    account_id = data.aws_caller_identity.keyman.account_id
    region = var.region
    cw_log_group = "/ecs/keyman-logs-${data.aws_caller_identity.keyman.account_id}"
  })
}

resource "aws_iam_instance_profile" "keyman_profile" {
  name = join("-", [local.keyman_id, "instance"])
  role = aws_iam_role.keyman_role.name
}

resource "aws_iam_role_policy_attachment" "cw_events" {
  role       = aws_iam_role.keyman_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceEventsRole"
}
