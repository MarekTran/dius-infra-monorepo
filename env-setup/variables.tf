# Global

variable "project_name" {
    description = "Root project name"
    type = string
    default = "llm-tool-registry"
}

variable "environment" {
    description = "Environment name (pg, prod)"
    type = string
}

variable "location" {
    description = "Deployment location"
    type = string
    default = "westeurope"
}

variable "tags" {
    description = "Global project tags"
    type = map(string)
    default = {}
}

# VNET

variable "subnets" {
    description = "VNET subnets"
    type = map(object({
        address_prefix = string
        delegation = optional(string)
    }))
    default = {}
}

# PostgreSQL

# ACR

variable "acr_sku_name" {
    description = "ACR Resource SKU"
    type = string
    default = "Basic"
}

variable "acr_admin_enabled" {
    description = "Enable ACR admin user"
    type = bool
    default = false
}

# AKS

variable "aks_node_count" {
    description = "AKS node count"
    type = number
    default = 2
}

variable "aks_node_vm_size" {
    description = "AKS node VM size"
    type = string
    default = "Standard_DS2_v2"
}

variable "aks_os_disk_size_gb" {
    description = "AKS node OS disk size in GB"
    type = number
    default = 30
}

