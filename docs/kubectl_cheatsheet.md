# kubectl Cheatsheet for CloudForge

## Context Management
```bash
# List all contexts
kubectl config get-contexts

# Switch to minikube
kubectl config use-context minikube

# Switch to EKS (after aws eks update-kubeconfig)
kubectl config use-context arn:aws:eks:eu-west-1:430695042642:cluster/cloudforge-production
```

## Pods
```bash
# List pods in namespace
kubectl get pods -n cloudforge

# Describe a pod (events, status, config)
kubectl describe pod <pod-name> -n cloudforge

# Get logs
kubectl logs <pod-name> -n cloudforge

# Follow logs
kubectl logs -f <pod-name> -n cloudforge

# Logs from all pods with label
kubectl logs -n cloudforge -l app=cloudforge

# Exec into a pod
kubectl exec -it <pod-name> -n cloudforge -- /bin/bash
```

## Deployments
```bash
# List deployments
kubectl get deployments -n cloudforge

# Scale manually
kubectl scale deployment cloudforge --replicas=3 -n cloudforge

# Rolling restart
kubectl rollout restart deployment/cloudforge -n cloudforge

# Check rollout status
kubectl rollout status deployment/cloudforge -n cloudforge

# Rollback
kubectl rollout undo deployment/cloudforge -n cloudforge
```

## Debugging
```bash
# Get all resources in namespace
kubectl get all -n cloudforge

# Describe service
kubectl describe service cloudforge -n cloudforge

# Check HPA status
kubectl get hpa -n cloudforge

# Get events
kubectl get events -n cloudforge --sort-by='.lastTimestamp'
```

## Helm
```bash
# List releases
helm list -n cloudforge

# Upgrade
helm upgrade cloudforge ./helm/cloudforge -n cloudforge

# Rollback
helm rollback cloudforge 1 -n cloudforge

# Uninstall
helm uninstall cloudforge -n cloudforge