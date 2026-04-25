# Kubernetes (K8s) — Quick Reference

## What is Kubernetes?

An open-source container orchestration platform. It automates deploying, scaling, and managing containerized applications. Originally designed by Google, now maintained by the Cloud Native Computing Foundation (CNCF).

## Core Concepts

### Pods
- Smallest deployable unit in K8s
- Contains one or more containers that share storage and network
- Ephemeral — they can be created and destroyed dynamically
- Each pod gets its own IP address within the cluster

### Deployments
- Manages a set of identical pods (replicas)
- Handles rolling updates and rollbacks
- Declares the desired state — K8s makes it happen
- Example: "I want 3 replicas of my web server running version 2.1"

### Services
- Provides a stable endpoint (IP + DNS name) for a set of pods
- Types: ClusterIP (internal), NodePort (external on node), LoadBalancer (cloud LB)
- Decouples frontend from backend — pods can come and go, the service stays

### ConfigMaps and Secrets
- ConfigMaps: store non-sensitive configuration as key-value pairs
- Secrets: store sensitive data (passwords, tokens) — base64 encoded
- Both can be mounted as files or injected as environment variables

### Namespaces
- Virtual clusters within a physical cluster
- Isolate resources between teams or environments (dev, staging, prod)
- Default namespace: `default`

## Key Commands

```bash
kubectl get pods                    # List all pods
kubectl get services                # List all services
kubectl describe pod <name>         # Detailed pod info
kubectl logs <pod-name>             # View pod logs
kubectl apply -f deployment.yaml    # Apply a configuration
kubectl delete pod <name>           # Delete a pod
kubectl scale deployment <name> --replicas=5  # Scale up
kubectl rollout status deployment <name>      # Check rollout
kubectl exec -it <pod> -- /bin/bash           # Shell into pod
```

## Architecture

### Control Plane
- **API Server**: frontend to the cluster, handles all REST requests
- **etcd**: distributed key-value store for all cluster data
- **Scheduler**: assigns pods to nodes based on resource availability
- **Controller Manager**: runs controllers (ReplicaSet, Deployment, etc.)

### Worker Nodes
- **kubelet**: agent that ensures containers are running in pods
- **kube-proxy**: handles networking rules for pod communication
- **Container runtime**: Docker, containerd, or CRI-O

## Common Misconceptions

1. "Kubernetes replaces Docker" — No, K8s orchestrates containers. Docker (or containerd) runs them.
2. "Pods are containers" — Pods contain containers. A pod can have multiple containers (sidecar pattern).
3. "Kubernetes is only for large scale" — It has overhead, but tools like k3s/minikube make it usable for small deployments.
4. "You need Kubernetes for everything" — Simple apps can run fine with Docker Compose or even a single VM.
