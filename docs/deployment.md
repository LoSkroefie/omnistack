# OmniStack Deployment Guide

## Deployment Options

OmniStack supports multiple deployment options:

1. Docker Compose (Development)
2. Kubernetes (Production)
3. Cloud Platforms (AWS, GCP, Azure)

## Prerequisites

- Docker and Docker Compose
- Kubernetes cluster (for production)
- Domain name and SSL certificates
- Infrastructure access (cloud credentials)
- CI/CD pipeline

## 1. Docker Compose Deployment

### Development Environment

1. Build and start services:
```bash
docker-compose up --build
```

2. Environment variables in `.env`:
```env
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
REDIS_URL=redis://redis:6379/0
```

3. Access services:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

### Production Environment

1. Use production compose file:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

2. Production environment variables:
```env
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
REDIS_URL=redis://redis:6379/0
SSL_CERT_PATH=/etc/ssl/certs/server.crt
SSL_KEY_PATH=/etc/ssl/private/server.key
```

## 2. Kubernetes Deployment

### Prerequisites

- Kubernetes cluster
- kubectl configured
- Helm installed
- Container registry access

### Deployment Steps

1. Build and push Docker images:
```bash
# Build images
docker build -t your-registry/omnistack-api:latest .

# Push to registry
docker push your-registry/omnistack-api:latest
```

2. Deploy using Helm:
```bash
# Add Helm repo
helm repo add omnistack https://charts.jvrsoftware.com

# Install chart
helm install omnistack omnistack/omnistack \
    --namespace omnistack \
    --create-namespace \
    --values values.yaml
```

3. Configure values.yaml:
```yaml
api:
  replicas: 3
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1Gi
  
redis:
  enabled: true
  persistence:
    size: 10Gi

monitoring:
  prometheus:
    enabled: true
  grafana:
    enabled: true

ingress:
  enabled: true
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: api.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: omnistack-tls
      hosts:
        - api.yourdomain.com
```

4. Apply manifests:
```bash
kubectl apply -f k8s/
```

### Monitoring Setup

1. Install monitoring stack:
```bash
helm install monitoring prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --create-namespace
```

2. Configure service monitors:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: omnistack
spec:
  selector:
    matchLabels:
      app: omnistack
  endpoints:
    - port: metrics
```

### Scaling

1. Horizontal scaling:
```bash
kubectl scale deployment omnistack-api --replicas=5
```

2. Vertical scaling:
```bash
kubectl edit deployment omnistack-api
```

## 3. Cloud Platform Deployment

### AWS Deployment

1. EKS Cluster Setup:
```bash
eksctl create cluster \
    --name omnistack \
    --region us-west-2 \
    --nodegroup-name standard-workers \
    --node-type t3.medium \
    --nodes 3 \
    --nodes-min 1 \
    --nodes-max 5
```

2. Configure AWS Load Balancer:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
spec:
  rules:
    - host: api.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: omnistack-api
                port:
                  number: 80
```

### GCP Deployment

1. GKE Cluster Setup:
```bash
gcloud container clusters create omnistack \
    --num-nodes 3 \
    --machine-type n1-standard-2 \
    --region us-central1
```

2. Configure Cloud Load Balancer:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: gce
spec:
  rules:
    - host: api.yourdomain.com
      http:
        paths:
          - path: /*
            backend:
              service:
                name: omnistack-api
                port:
                  number: 80
```

## Security Considerations

### 1. SSL/TLS Configuration

1. Generate certificates:
```bash
certbot certonly --dns-cloudflare \
    -d api.yourdomain.com \
    --email admin@yourdomain.com
```

2. Configure in Kubernetes:
```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: omnistack-tls
spec:
  secretName: omnistack-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - api.yourdomain.com
```

### 2. Network Security

1. Network policies:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
spec:
  podSelector:
    matchLabels:
      app: omnistack-api
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8000
```

### 3. Secrets Management

1. Create secrets:
```bash
kubectl create secret generic omnistack-secrets \
    --from-literal=jwt-secret=$(openssl rand -hex 32) \
    --from-literal=redis-password=$(openssl rand -hex 32)
```

2. Use in deployment:
```yaml
env:
  - name: JWT_SECRET
    valueFrom:
      secretKeyRef:
        name: omnistack-secrets
        key: jwt-secret
```

## Monitoring and Logging

### 1. Prometheus Setup

1. Install Prometheus Operator:
```bash
helm install prometheus prometheus-community/kube-prometheus-stack
```

2. Configure monitoring:
```yaml
prometheus:
  prometheusSpec:
    serviceMonitorSelector:
      matchLabels:
        app: omnistack
```

### 2. Logging Setup

1. Install EFK stack:
```bash
helm install logging elastic/eck-operator
```

2. Configure logging:
```yaml
filebeat:
  inputs:
    - type: container
      paths:
        - /var/log/containers/*.log
```

### 3. Alerting

1. Configure alerts:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: omnistack-alerts
spec:
  groups:
    - name: omnistack
      rules:
        - alert: HighErrorRate
          expr: rate(http_requests_total{status=~"5.."}[5m]) > 1
          for: 5m
          labels:
            severity: critical
```

## Backup and Recovery

### 1. Database Backups

1. Configure automated backups:
```bash
kubectl apply -f k8s/backup-cronjob.yaml
```

2. Backup CronJob:
```yaml
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: database-backup
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: backup
              image: postgres:13
              command: ["pg_dump"]
```

### 2. Recovery Procedures

1. Restore from backup:
```bash
kubectl exec -it postgres-0 -- psql -U postgres -f /backup/dump.sql
```

## Maintenance

### 1. Updates and Upgrades

1. Update application:
```bash
helm upgrade omnistack omnistack/omnistack \
    --values values.yaml \
    --set image.tag=new-version
```

2. Update dependencies:
```bash
helm dependency update
```

### 2. Health Checks

1. Configure readiness probe:
```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

2. Configure liveness probe:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 20
```

## Troubleshooting

### 1. Common Issues

1. Check pod status:
```bash
kubectl get pods -n omnistack
kubectl describe pod <pod-name>
```

2. View logs:
```bash
kubectl logs -f deployment/omnistack-api
```

### 2. Debug Tools

1. Deploy debug pod:
```bash
kubectl run debug --rm -i --tty \
    --image=nicolaka/netshoot \
    -- /bin/bash
```

2. Network debugging:
```bash
kubectl exec -it debug -- curl http://omnistack-api:8000/health
```

## Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
- [GCP GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
