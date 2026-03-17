# IAM policy for X-Ray
resource "aws_iam_policy" "xray_access" {
  name = "${var.app_name}-xray-access-${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords",
          "xray:GetSamplingRules",
          "xray:GetSamplingTargets",
          "xray:GetSamplingStatisticSummaries"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "xray_access" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = aws_iam_policy.xray_access.arn
}

# X-Ray sampling rule — sample 5% of requests in production
# 100% during development
resource "aws_xray_sampling_rule" "main" {
  rule_name      = "${var.app_name}-${var.environment}"
  priority       = 1000
  reservoir_size = 5
  fixed_rate     = 0.05
  url_path       = "*"
  host           = "*"
  http_method    = "*"
  service_type   = "*"
  service_name   = "cloudforge"
  resource_arn   = "*"
  version        = 1

  attributes = {}
}