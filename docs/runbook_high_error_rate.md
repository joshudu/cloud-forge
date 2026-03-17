# Runbook: High Error Rate

## Severity
P2 — Partial service degradation

## Symptoms
- CloudWatch alarm firing: >5 5xx errors in 5 minutes
- Some API requests returning 500
- Users reporting errors intermittently

## Detection
- CloudWatch alarm: `cloudforge-staging-5xx-errors`
- CloudWatch logs: filter for `"level":"ERROR"`
- Request error rate > 1% in CloudWatch dashboard

## Immediate Actions (first 5 minutes)

### 1. Identify the failing endpoint
CloudWatch Logs Insights query:
```
fields @timestamp, path, status_code, message
| filter status_code >= 500
| stats count() by path
| sort count desc
| limit 10
```

### 2. Check recent deployments
Was there a deployment in the last 30 minutes?
If yes — consider rolling back:
Go to ECS → Task Definitions → select previous revision
Update service to use previous task definition

### 3. Check downstream dependencies
- RDS: is `/health/ready` returning 200?
- Redis: are there cache errors in logs?
- SQS: are there messages piling up in the DLQ?

### 4. Check ECS task health
Are tasks restarting? Check ECS service events tab.
If tasks are crash-looping, check CloudWatch logs for startup errors.

## Recovery Verification
- Error rate drops below 1% in CloudWatch dashboard
- CloudWatch alarm returns to OK state
- `/health/ready` returns 200

## Post-Incident
- File a post-mortem using docs/post_mortem_template.md
- Add a test that would have caught this bug
- Review deployment process