# CloudForge SLO Definitions

## Service Level Indicators (SLIs)

### Availability SLI
Percentage of HTTP requests that return a non-5xx response.
Measured over a rolling 30-day window.

### Latency SLI
Percentage of HTTP requests that complete in under 500ms.
Measured at the 99th percentile over a rolling 30-day window.

### Error Rate SLI
Percentage of HTTP requests that return a 5xx response.
Measured over a rolling 24-hour window.

## Service Level Objectives (SLOs)

| SLI | Target | Measurement Window |
|-----|--------|-------------------|
| Availability | 99.5% | 30 days |
| Latency p99 < 500ms | 95% | 30 days |
| Error Rate < 1% | 99% | 24 hours |

## Error Budgets

### Availability Error Budget
- Target: 99.5% availability over 30 days
- Allowed downtime: 0.5% of 30 days = 3.6 hours per month
- When budget is exhausted: freeze non-critical deployments

### Latency Error Budget
- Target: 95% of requests under 500ms
- Allowed slow requests: 5% of total requests
- When budget is exhausted: performance review before next release

## SLA (External Commitment)
CloudForge does not currently have an external SLA.
Internal SLOs are used to guide reliability decisions.
In a production product, SLA would be a subset of SLO targets
with financial penalties for breach.

## CloudWatch Implementation
Current monitoring covers:
- Error rate via 5xx alarm (fires at >5 errors in 5 minutes)
- Request count via custom metric

Gaps to address:
- Latency percentile tracking not yet implemented
- Availability calculation not automated
- Error budget burn rate not tracked