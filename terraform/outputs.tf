output "keyman_iam_role_name" {
    description = "keyman iam role"
    value       = aws_iam_role.keyman_role.name
}

output "keyman_iam_role_arn" {
    description = "keyman iam role"
    value       = aws_iam_role.keyman_role.arn
}

output "keyman_fargate_cluster_id" {
    description = "keyman farget cluster ID"
    value       = aws_ecs_cluster.keyman.id
}

output "keyman_fargate_cluster_arn" {
    description = "keyman farget cluster ID"
    value       = aws_ecs_cluster.keyman.arn
}

output "keyman_cw_log_group" {
    description = "Cloudwatch log group"
    value       = aws_cloudwatch_log_group.keyman_logs.arn
}