# AKS

output "aks_kube_config" {
    description = "AKS kubeconfig for kubectl access"
    value = module.kubernetes.kube_config
    sensitive = true
}

output "aks_host" {
    description = "AKS API server host"
    value = module.kubernetes.host
    sensitive = true
}

# ACR

output "acr_login_server" {
    description = "ACR login server URL"
    value = module.azure_container_registry.fqdn
}

