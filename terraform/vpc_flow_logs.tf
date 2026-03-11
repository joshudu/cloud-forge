# IAM role for VPC Flow Logs to write to CloudWatch
resource "aws_iam_role" "vpc_flow_logs" {
  name = "${var.app_name}-vpc-flow-logs-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "vpc_flow_logs" {
  name = "${var.app_name}-vpc-flow-logs-${var.environment}"
  role = aws_iam_role.vpc_flow_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = "*"
      }
    ]
  })
}

# CloudWatch log group for VPC flow logs
resource "aws_cloudwatch_log_group" "vpc_flow_logs" {
  name              = "/vpc/flow-logs/${var.app_name}-${var.environment}"
  retention_in_days = 7
}

# Enable flow logs on the default VPC
resource "aws_flow_log" "main" {
  vpc_id          = data.aws_vpc.default.id
  traffic_type    = "ALL"
  iam_role_arn    = aws_iam_role.vpc_flow_logs.arn
  log_destination = aws_cloudwatch_log_group.vpc_flow_logs.arn

  tags = {
    Name        = "${var.app_name}-${var.environment}"
    Environment = var.environment
  }
}