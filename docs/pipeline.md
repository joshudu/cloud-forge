# CloudForge CI/CD Pipeline

## Pipeline Stages
```
git push → test → security-scan → staging → [approval] → production
```

## Stage Details

### Test
- Runs pytest with fake DATABASE_URL and JWT_SECRET_KEY
- Fails build if any test fails
- Skips chaos tests (marked with @pytest.mark.chaos)

### Security Scan
- Builds Docker image locally in CI runner
- Runs Trivy vulnerability scanner
- Fails build on CRITICAL severity CVEs
- Ignores unfixed vulnerabilities

### Staging Deployment
- Builds and pushes Docker image to ECR with git SHA tag
- Updates ECS task definition with new image
- Waits for ECS service to stabilise
- Automatic — no approval required

### Production Deployment
- Requires manual approval from repository owner
- Uses same image already deployed to staging
- Currently a placeholder — staging serves as production

## Deployment Strategy
ECS rolling deployment — new tasks start before old tasks stop.
Zero downtime for stateless services.

## Rollback
To roll back to a previous version:
1. Find the previous git SHA from ECR image tags
2. Update ECS task definition manually with that image tag
3. Or revert the commit and push — pipeline redeploys automatically