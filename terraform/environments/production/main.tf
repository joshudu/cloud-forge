terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "cloudforge-terraform-state-430695042642"
    key            = "production/terraform.tfstate"
    region         = "eu-west-1"
    dynamodb_table = "cloudforge-terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}