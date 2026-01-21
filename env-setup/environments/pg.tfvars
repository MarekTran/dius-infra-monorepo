# Global

environment = "pg"
location = "westeurope"
tags = {
    environment = "pg"
    project = "jarvis-tools"
}
project_name = "jarvis-tools"

# VNET

subnets = {
    aks = {
        address_prefix = "10.10.0.0/18"
    }
}

aks_os_disk_size_gb = 128