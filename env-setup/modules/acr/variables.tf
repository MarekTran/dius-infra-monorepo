# Global

variable "rg_name" {
    description = "Resource group name for deployment"
    type = string
}

variable "name" {
    description = "Resource name"
    type = string
}

variable "location" {
    description = "Deployment location"
    type = string
    default = "westeurope"
}

variable "tags" {
    description = "Resource tags"
    type = map(string)
    default = {}
}

variable "sku_name" {
    description = "Resource SKU"
    type = string
    default = "Basic"
}

# Resource specific

variable "admin_enabled" {
    description = "Enable admin user"
    type = bool
    default = false
}
