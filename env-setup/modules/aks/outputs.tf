output "id" {
    value = azurerm_kubernetes_cluster.this.id
}

output "name" {
    value = azurerm_kubernetes_cluster.this.name
}

output "kube_config" {
    value = azurerm_kubernetes_cluster.this.kube_config_raw
    sensitive = true
}

output "kubelet_identity" {
    value = azurerm_kubernetes_cluster.this.kubelet_identity[0].object_id
}

output "host" {
    value = azurerm_kubernetes_cluster.this.kube_config[0].host
    sensitive = true
}

output "key_vault_secrets_provider_identity" {
    value = azurerm_kubernetes_cluster.this.key_vault_secrets_provider[0].secret_identity[0].object_id
}
