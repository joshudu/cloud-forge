# Metric filter — counts 5xx errors from ECS logs
resource "aws_cloudwatch_log_metric_filter" "error_rate" {
  name           = "${var.app_name}-5xx-errors-${var.environment}"
  log_group_name = aws_cloudwatch_log_group.app.name
  pattern        = "{ $.status_code >= 500 }"

  metric_transformation {
    name      = "5xxErrorCount"
    namespace = "CloudForge/${var.environment}"
    value     = "1"
    default_value = "0"
  }
}

# Metric filter — counts all requests
resource "aws_cloudwatch_log_metric_filter" "request_count" {
  name           = "${var.app_name}-request-count-${var.environment}"
  log_group_name = aws_cloudwatch_log_group.app.name
  pattern        = "{ $.status_code > 0 }"

  metric_transformation {
    name      = "RequestCount"
    namespace = "CloudForge/${var.environment}"
    value     = "1"
    default_value = "0"
  }
}

# Alarm — fires when error rate exceeds 1% over 5 minutes
resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  alarm_name          = "${var.app_name}-high-error-rate-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "5xxErrorCount"
  namespace           = "CloudForge/${var.environment}"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "More than 5 errors in 5 minutes"
  treat_missing_data  = "notBreaching"

  tags = {
    Name        = "${var.app_name}-high-error-rate-${var.environment}"
    Environment = var.environment
  }
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.app_name}-${var.environment}"

  dashboard_body = jsonencode({
    widgets = [
      {
        "type" : "metric",
        "x" : 0,
        "y" : 0,
        "width" : 12,
        "height" : 6,
        "properties" : {
          "region" : "eu-west-2",
          "title" : "Request Count",
          "period" : 60,
          "stat" : "Sum",
          "metrics" : [
            [ "CloudForge/${var.environment}", "RequestCount" ]
          ]
        }
      },
      {
        "type" : "metric",
        "x" : 0,
        "y" : 6,
        "width" : 12,
        "height" : 6,
        "properties" : {
          "region" : "eu-west-2",
          "title" : "5xx Error Count",
          "period" : 60,
          "stat" : "Sum",
          "metrics" : [
            [ "CloudForge/${var.environment}", "5xxErrorCount" ]
          ]
        }
      }
    ]
  })
}
