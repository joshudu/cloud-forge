# Dead letter queue — messages that fail processing go here
resource "aws_sqs_queue" "events_dlq" {
  name                      = "${var.app_name}-events-dlq-${var.environment}"
  message_retention_seconds = 1209600  # 14 days

  tags = {
    Name        = "${var.app_name}-events-dlq-${var.environment}"
    Environment = var.environment
  }
}

# Main events queue
resource "aws_sqs_queue" "events" {
  name                       = "${var.app_name}-events-${var.environment}"
  visibility_timeout_seconds = 30
  message_retention_seconds  = 86400  # 1 day

  # After 3 failed processing attempts, move to DLQ
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.events_dlq.arn
    maxReceiveCount     = 3
  })

  tags = {
    Name        = "${var.app_name}-events-${var.environment}"
    Environment = var.environment
  }
}

output "sqs_queue_url" {
  value = aws_sqs_queue.events.url
}

output "sqs_dlq_url" {
  value = aws_sqs_queue.events_dlq.url
}