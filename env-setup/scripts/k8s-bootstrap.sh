ENVIRONMENT=${1:-pg}
PROJECT_NAME="jarvis-tools"
RESOURCE_GROUP="${PROJECT_NAME}-${ENVIRONMENT}-infra-rg"
GITOPS_DIR="../../gitops"
AKS_NAME="${PROJECT_NAME}-${ENVIRONMENT}-aks"

az aks get-credentials --resource-group "$RESOURCE_GROUP" --name "$AKS_NAME" --overwrite-existing

kubectl cluster-info

echo ""
echo "=== Installing ArgoCD ==="
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

echo "Waiting for ArgoCD to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd

echo ""
echo "=== Installing traefik ==="
helm repo add traefik https://traefik.github.io/charts
helm repo update
helm install traefik traefik/traefik --wait --timeout 300s

echo ""                                                                                                                                        
echo "=== Adding Git repo credentials ==="                                                                                                     
kubectl create secret generic repo-dius-infra \
  -n argocd \
  --from-file=sshPrivateKey="$HOME/.ssh/dius-infra-monorepo-key" \
  --from-literal=url=git@github.com:MarekTran/dius-infra-monorepo.git \
  --from-literal=type=git \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl label secret repo-dius-infra -n argocd argocd.argoproj.io/secret-type=repository --overwrite

echo ""
echo "=== Bootstrapping ArgoCD ==="
kubectl apply -f "$GITOPS_DIR/argocd/project.yaml"
kubectl apply -f "$GITOPS_DIR/argocd/bootstrap.yaml"

