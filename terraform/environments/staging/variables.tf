variable "aws_region" {
  default = "eu-west-1"
}

variable "app_name" {
  default = "cloudforge"
}

variable "environment" {
  default = "staging"
}

variable "db_username" {
  sensitive = true
}

variable "db_password" {
  sensitive = true
}