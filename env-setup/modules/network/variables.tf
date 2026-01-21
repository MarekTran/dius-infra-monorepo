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

# Resource specific

variable "address_space" {
    description = "VNET address space"
    type = list(string)
    default = ["10.10.0.0/16"]
}

variable "subnets" {
    description = "VNET subnets"
    type = map(object({
        address_prefix = string
        delegation = optional(string) 
    }))
    default = {}
}