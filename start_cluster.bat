@echo off
REM ===============================
REM FastAPI Kubernetes Microservice Setup
REM ===============================

echo Starting Minikube...
minikube start --driver=docker

echo Building FastAPI Docker image from backend folder...
docker build -t fastapi-k8s .\backend

echo Loading Docker image into Minikube...
minikube image load fastapi-k8s:latest

echo Adding Helm repo for Prometheus/Grafana...
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

echo Deploying FastAPI app from Helm chart (fastapi-app folder)...
helm upgrade --install my-fastapi .\fastapi-app -n fastapi-app --create-namespace ^
  --set kube-prometheus-stack.grafana.enabled=true ^
  --set kube-prometheus-stack.grafana.service.type=NodePort ^
  --set kube-prometheus-stack.grafana.service.nodePort=30000 ^
  --set kube-prometheus-stack.prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false

echo Opening Grafana UI...
start http://localhost:30000

echo FastAPI UI should be available at http://micro.local
pause
