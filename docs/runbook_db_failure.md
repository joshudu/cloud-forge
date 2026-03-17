# Runbook: Database Connection Failure

## Severity
P1 — All API requests failing

## Symptoms
- `/health/ready` returning 503
- CloudWatch alarm firing: >5 errors in 5 minutes
- Application logs showing: `OperationalError: connection refused`
- ECS tasks restarting repeatedly

## Detection
- CloudWatch alarm: `cloudforge-staging-5xx-errors`
- CloudWatch logs: filter for `"OperationalError"`
- `/health/ready` endpoint returning 503

## Immediate Actions (first 5 minutes)

### 1. Verify RDS status
Go to AWS Console → RDS → Databases → cloudforge-staging
Check: Is the instance Available, Stopped, or in an error state?

### 2. If RDS is Stopped
Click Actions → Start
Wait 3-5 minutes for RDS to become Available
ECS tasks will recover automatically via pool_pre_ping

### 3. If RDS is Available but app cannot connect
Check security group rules — port 5432 must allow inbound from ECS tasks
Check RDS parameter group — max_connections setting
Check ECS task environment variable DATABASE_URL is correct

### 4. If RDS is in an error state
Check RDS events for the failure reason
Consider restoring from automated backup if data corruption suspected

## Recovery Verification
- `/health/ready` returns 200
- CloudWatch logs show successful DB connections
- No 5xx errors in CloudWatch metrics for 5 minutes

## Post-Incident
- File a post-mortem using docs/post_mortem_template.md
- Review RDS automated backup retention settings
- Consider Multi-AZ deployment to prevent single point of failure

## Prevention
- Enable RDS Multi-AZ (Week 12)
- Set CloudWatch alarm for RDS CPU > 80%
- Set CloudWatch alarm for RDS connections > 80% of max