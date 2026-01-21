# LLM Tool Registry - Infra

terraform {
    required_providers {
        azurerm = {
            source = "hashicorp/azurerm"
            version = "~> 3.75"
        }
    }
    required_version = ">= 1.1.0"
}

provider "azurerm" {
    features {}
}

data "azurerm_client_config" "current" {}

locals {
    rg_name_infra = "${var.project_name}-${var.environment}-infra-rg"
    rg_name_nw = "${var.project_name}-${var.environment}-nw-rg"
    vnet_name = "${var.project_name}-${var.environment}-vnet"
    acr_name = "jarvistools"
    aks_name = "${var.project_name}-${var.environment}-aks"
    subnets = {
        for k, v in var.subnets : "${var.project_name}-${var.environment}-${k}-subnet" => v
    }
}

module "rg_infra" {
    source = "./modules/resource-group"

    name = local.rg_name_infra
    location = var.location
    tags = var.tags
}

module "rg_nw" {
    source = "./modules/resource-group"

    name = local.rg_name_nw
    location = var.location
    tags = var.tags
}

module "vnet" {
    source = "./modules/network"

    rg_name = module.rg_nw.name
    name = local.vnet_name
    location = var.location
    tags = var.tags

    subnets = local.subnets
}

module "azure_container_registry" {
    source = "./modules/acr"

    rg_name = local.rg_name_infra
    name = local.acr_name
    location = var.location
    tags = var.tags

    sku_name = var.acr_sku_name
    admin_enabled = var.acr_admin_enabled
}

module "kubernetes" {
    source = "./modules/aks"

    rg_name = local.rg_name_infra
    name = local.aks_name
    location = var.location
    tags = var.tags

    dns_prefix = "${var.project_name}-${var.environment}-aks"

    node_count = var.aks_node_count
    vm_size = var.aks_node_vm_size
    os_disk_size_gb = var.aks_os_disk_size_gb

    subnet_id = module.vnet.subnet_ids["${var.project_name}-${var.environment}-aks-subnet"]
}

resource "azurerm_role_assignment" "aks_acr" {
    principal_id = module.kubernetes.kubelet_identity
    role_definition_name = "AcrPull"
    scope = module.azure_container_registry.id
    skip_service_principal_aad_check = true
}