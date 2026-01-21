# Global

variable "name" {
    description = "Resource name"
    type = string
    default = "llm-tool-registry-rg"
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