output "id" {
    value = azurerm_virtual_network.this.id
}

output "name" {
    value = azurerm_virtual_network.this.name
}

output "location" {
    value = azurerm_virtual_network.this.location
}

output "tags" {
    value = azurerm_virtual_network.this.tags
}

output "subnet_ids" {
    value = { for k, v in azurerm_subnet.this : k => v.id}
}