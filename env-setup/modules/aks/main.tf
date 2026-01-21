resource "azurerm_kubernetes_cluster" "this" {
    name = var.name
    location = var.location
    resource_group_name = var.rg_name
    dns_prefix = var.dns_prefix
    kubernetes_version = var.kubernetes_version
    tags = var.tags

    default_node_pool {
        name = "default"
        node_count = var.node_count
        vm_size = var.vm_size
        os_disk_size_gb = var.os_disk_size_gb
        vnet_subnet_id = var.subnet_id
    }

    identity {
        type = "SystemAssigned"
    }

    network_profile {
        network_plugin = "azure"
    }

    key_vault_secrets_provider {
        secret_rotation_enabled = true
        secret_rotation_interval = "2m"
    }
}
