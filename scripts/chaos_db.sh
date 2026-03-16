#!/bin/bash
# Chaos test — stop RDS for 30 seconds and measure recovery
# Run this manually: bash scripts/chaos_db.sh

ECS_IP="34.247.28.76"  # Replace with your ECS IP
DB_INSTANCE="cloudforge-staging"
REGION="eu-west-1"

echo "Starting chaos test — stopping RDS for 30 seconds"
echo "Monitoring /health/ready every 5 seconds"

# Stop RDS
aws rds stop-db-instance \
  --db-instance-identifier $DB_INSTANCE \
  --region $REGION > /dev/null 2>&1

echo "RDS stop initiated"

# Monitor health for 90 seconds
for i in {1..18}; do
  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    http://$ECS_IP:8000/health/ready --max-time 5)
  TIMESTAMP=$(date +"%H:%M:%S")
  echo "$TIMESTAMP — /health/ready returned: $RESPONSE"
  sleep 5
done

echo ""
echo "Starting RDS again"
aws rds start-db-instance \
  --db-instance-identifier $DB_INSTANCE \
  --region $REGION > /dev/null 2>&1

echo "RDS start initiated — monitoring recovery"

# Monitor recovery for 5 minutes
for i in {1..60}; do
  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    http://$ECS_IP:8000/health/ready --max-time 5)
  TIMESTAMP=$(date +"%H:%M:%S")
  echo "$TIMESTAMP — /health/ready returned: $RESPONSE"
  if [ "$RESPONSE" = "200" ]; then
    echo ""
    echo "Recovery confirmed at $TIMESTAMP"
    exit 0
  fi
  sleep 5
done

echo "Recovery not confirmed within 5 minutes"
exit 1