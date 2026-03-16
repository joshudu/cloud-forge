# Subnet group for ElastiCache
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.app_name}-cache-${var.environment}"
  subnet_ids = data.aws_subnets.default.ids

  tags = {
    Name        = "${var.app_name}-cache-${var.environment}"
    Environment = var.environment
  }
}

# Security group for Redis
resource "aws_security_group" "redis" {
  name        = "${var.app_name}-redis-${var.environment}"
  description = "Allow Redis access from ECS tasks only"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.app_name}-redis-${var.environment}"
    Environment = var.environment
  }
}

# ElastiCache Redis cluster
resource "aws_elasticache_cluster" "main" {
  cluster_id           = "${var.app_name}-${var.environment}"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  engine_version       = "7.0"
  port                 = 6379

  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]

  tags = {
    Name        = "${var.app_name}-${var.environment}"
    Environment = var.environment
  }
}

output "redis_endpoint" {
  value     = aws_elasticache_cluster.main.cache_nodes[0].address
  sensitive = true
}