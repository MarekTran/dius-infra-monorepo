output "id" {
    value = azurerm_container_registry.this.id
}

output "name" {
    value = azurerm_container_registry.this.name
}

output "location" {
    value = azurerm_container_registry.this.location
}

output "tags" {
    value = azurerm_container_registry.this.tags
}

output "fqdn" {
    value = azurerm_container_registry.this.login_server
}