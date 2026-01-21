resource "azurerm_container_registry" "this" {
    name = var.name
    resource_group_name = var.rg_name
    location = var.location
    sku = var.sku_name
    admin_enabled = var.admin_enabled
    tags = var.tags
}

