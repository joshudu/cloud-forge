# ECS to EKS Migration Plan

## Concept Mapping

| ECS Concept | Kubernetes Equivalent |
|-------------|----------------------|
| Cluster | Cluster |
| Service | Deployment + Service |
| Task Definition | Pod Spec |
| Task | Pod |
| ECR | ECR (unchanged) |
| ALB Target Group | Ingress + Service |
| ECS Autoscaling | HorizontalPodAutoscaler |
| ECS Task Role | ServiceAccount + IAM Role (IRSA) |
| CloudWatch Logs | CloudWatch Container Insights or Fluentd |
| Fargate | EKS Fargate Profile |
| Secrets Manager | External Secrets Operator |

## What Changes

### Infrastructure
- Replace ECS cluster with EKS cluster (Terraform `aws_eks_cluster`)
- Replace ECS service with Kubernetes Deployment
- Replace ECS task definition with Pod spec in Deployment
- Replace ECS autoscaling with HorizontalPodAutoscaler
- Add AWS Load Balancer Controller to handle Ingress
- Add External Secrets Operator for Secrets Manager integration
- Replace ECS task role with IRSA (IAM Roles for Service Accounts)

### Application Code
- No application code changes required
- FastAPI runs identically in a Pod as in an ECS task
- Same Docker image, same ECR repository

### CI/CD Pipeline
- Replace `aws-actions/amazon-ecs-deploy-task-definition` with `kubectl apply` or `helm upgrade`
- Add kubeconfig setup step to GitHub Actions
- Add `aws eks update-kubeconfig` to pipeline

### Secrets Management
- Replace ECS environment variable injection from Secrets Manager
- Install External Secrets Operator in EKS
- Create ExternalSecret resources pointing to AWS Secrets Manager
- Secrets sync automatically into Kubernetes Secrets

## What Stays the Same
- Docker image and ECR repository unchanged
- RDS database unchanged — connection string identical
- ElastiCache Redis unchanged
- SQS queues unchanged
- CloudWatch logging unchanged
- Application code entirely unchanged

## Migration Steps

### Step 1 — Provision EKS cluster via Terraform
```hcl
module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  cluster_name    = "cloudforge-production"
  cluster_version = "1.29"
  vpc_id          = data.aws_vpc.default.id
  subnet_ids      = data.aws_subnets.default.ids

  eks_managed_node_groups = {
    main = {
      min_size     = 2
      max_size     = 10
      desired_size = 2
      instance_types = ["t3.medium"]
    }
  }
}
```

### Step 2 — Install AWS Load Balancer Controller
Handles Ingress resources and provisions ALBs automatically.

### Step 3 — Install External Secrets Operator
Syncs secrets from AWS Secrets Manager into Kubernetes Secrets.

### Step 4 — Deploy CloudForge via Helm
```bash
helm upgrade --install cloudforge ./helm/cloudforge \
  --namespace cloudforge \
  --set image.repository=430695042642.dkr.ecr.eu-west-1.amazonaws.com/cloudforge-staging \
  --set image.tag=$IMAGE_TAG
```

### Step 5 — Update CI/CD pipeline
Replace ECS deploy action with helm upgrade in GitHub Actions.

### Step 6 — DNS cutover
Point Route53 records from ECS ALB to EKS ALB.
Zero downtime if done with weighted routing.

## Why EKS Over ECS

| Factor | ECS | EKS |
|--------|-----|-----|
| Learning curve | Low | High |
| Vendor lock-in | High (AWS only) | Low (K8s is portable) |
| Ecosystem | Limited | Vast |
| Job market | Moderate | Very high demand |
| Operational overhead | Low | Higher |
| Fine-grained control | Limited | Full |

For a learning project, ECS was the right starting point.
For production at scale, EKS gives more control and portability.
For interviews, knowing both and being able to explain the tradeoffs is what matters.

## Estimated Migration Effort
- Infrastructure (Terraform): 2 days
- CI/CD pipeline updates: 1 day
- Testing and validation: 2 days
- DNS cutover: 1 hour
- Total: approximately 5 days for an experienced engineer