# CloudForge Security Posture

## NIST Cybersecurity Framework Mapping

### Identify
- Asset inventory: All infrastructure defined in Terraform
- Data classification: Tenant PII stored in isolated PostgreSQL schemas
- Risk assessment: OWASP Top 10 reviewed and mapped to controls below

### Protect
- Authentication: JWT with short expiry (30 minutes) and refresh tokens
- Authorisation: Schema-per-tenant isolation enforced at DB session level
- Rate limiting: Per-tenant rate limits on auth endpoints (5/min register, 10/min login)
- Encryption in transit: TLS enforced on RDS, HTTPS on all endpoints
- CORS: Explicitly configured, no wildcard origins
- Secrets management: AWS Secrets Manager, no secrets in code or env vars in production

### Detect
- Logging: Structured JSON logs with request ID and tenant context
- Monitoring: CloudWatch dashboards for request rate and error rate
- Alerting: CloudWatch alarm fires on >5 errors in 5 minutes
- Threat detection: AWS GuardDuty enabled on all data sources
- Network monitoring: VPC Flow Logs capturing all traffic

### Respond
- Incident runbook: See docs/runbook_db_failure.md (Week 11)
- GDPR erasure: DELETE /admin/tenants/{id} drops tenant schema and all data
- Audit trail: All erasure events logged with operator identity

### Recover
- Infrastructure as code: Full environment reproducible with terraform apply
- Database backups: RDS automated backups enabled (7 day retention)
- CI/CD: Automated deployment pipeline with rollback capability

## OWASP Top 10 Controls

| Risk | Control |
|------|---------|
| A01 Broken Access Control | Schema-per-tenant, JWT tenant claim validation |
| A02 Cryptographic Failures | bcrypt for passwords, TLS for transport |
| A03 Injection | SQLAlchemy parameterised queries |
| A04 Insecure Design | Repository pattern, separation of concerns |
| A05 Security Misconfiguration | Terraform-managed infrastructure, no defaults |
| A06 Vulnerable Components | ECR scan on push, Trivy in pipeline (Week 7) |
| A07 Auth Failures | Rate limiting, JWT expiry, refresh tokens |
| A08 Data Integrity Failures | Pydantic validation on all inputs |
| A09 Logging Failures | Structured logging on every request |
| A10 SSRF | Not applicable — no user-controlled URLs |

## GDPR Controls

- Data minimisation: User model collects only email and hashed password
- Right to erasure: Implemented via tenant schema drop
- Data residency: All data in eu-west-1
- Encryption at rest: RDS encryption enabled