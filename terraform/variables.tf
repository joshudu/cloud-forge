variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-1"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "cloudforge"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "staging"
}