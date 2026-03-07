# DB Subnet Group — RDS needs to know which subnets it can live in
resource "aws_db_subnet_group" "main" {
  name       = "${var.app_name}-${var.environment}"
  subnet_ids = data.aws_subnets.default.ids

  tags = {
    Name        = "${var.app_name}-${var.environment}"
    Environment = var.environment
  }
}

# Security group for RDS — only ECS tasks can connect
resource "aws_security_group" "rds" {
  name        = "${var.app_name}-rds-${var.environment}"
  description = "Allow PostgreSQL access from ECS tasks only"
  vpc_id      = data.aws_vpc.default.id

ingress {
  from_port       = 5432
  to_port         = 5432
  protocol        = "tcp"
  security_groups = [aws_security_group.ecs_tasks.id]
}

ingress {
  from_port   = 5432
  to_port     = 5432
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.app_name}-rds-${var.environment}"
    Environment = var.environment
  }
}

# RDS PostgreSQL instance
resource "aws_db_instance" "main" {
  identifier        = "${var.app_name}-${var.environment}"
  engine            = "postgres"
  engine_version    = "15.17"
  instance_class    = "db.t3.micro"
  allocated_storage = 20

  db_name  = "cloudforge"
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  publicly_accessible = true
  skip_final_snapshot = true  # only for staging — never in production
  multi_az            = false # staging only

  tags = {
    Name        = "${var.app_name}-${var.environment}"
    Environment = var.environment
  }
}