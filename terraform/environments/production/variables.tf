variable "aws_region" {
  default = "eu-west-1"
}

variable "app_name" {
  default = "cloudforge"
}

variable "environment" {
  default = "production"
}

variable "db_username" {
  sensitive = true
}

variable "db_password" {
  sensitive = true
}