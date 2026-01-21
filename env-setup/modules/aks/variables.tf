# Global

variable "rg_name" {
    description = "Resource group name for deployment"
    type = string
}

variable "name" {
    description = "AKS cluster name"
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

# AKS specific

variable "dns_prefix" {
    description = "DNS prefix for the cluster"
    type = string
}

variable "kubernetes_version" {
    description = "Kubernetes version"
    type = string
    default = null
}

variable "subnet_id" {
    description = "Subnet ID for AKS nodes"
    type = string
}

variable "vm_size" {
    description = "VM size for default node pool"
    type = string
    default = "Standard_DS2_v2"
}

variable "node_count" {
    description = "Number of nodes in default pool"
    type = number
    default = 2
}

variable "os_disk_size_gb" {
    description = "OS disk size in GB"
    type = number
    default = 30
}
