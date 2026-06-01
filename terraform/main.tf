###############################################################################
# Test fixtures for azure-orphan-cleaner.
#
# Creates three deliberately ORPHANED resources so you can verify detection:
#   1. An unattached managed disk
#   2. A disconnected (unassociated) public IP
#   3. A NIC with no VM attached
#
# Usage:
#   az login
#   terraform init
#   terraform apply        # creates the orphans
#   az orphan scan --type all --estimate-cost
#   terraform destroy      # cleans everything up
###############################################################################

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
}

provider "azurerm" {
  features {}
}

variable "location" {
  type    = string
  default = "eastus"
}

resource "azurerm_resource_group" "orphan_test" {
  name     = "rg-orphan-cleaner-test"
  location = var.location
}

# 1. Unattached managed disk -------------------------------------------------
resource "azurerm_managed_disk" "orphan_disk" {
  name                 = "orphan-test-disk"
  location             = azurerm_resource_group.orphan_test.location
  resource_group_name  = azurerm_resource_group.orphan_test.name
  storage_account_type = "Standard_LRS"
  create_option        = "Empty"
  disk_size_gb         = 32
  # Never attached to a VM -> diskState == 'Unattached'
}

# 2. Disconnected public IP --------------------------------------------------
resource "azurerm_public_ip" "orphan_pip" {
  name                = "orphan-test-pip"
  location            = azurerm_resource_group.orphan_test.location
  resource_group_name = azurerm_resource_group.orphan_test.name
  allocation_method   = "Static"
  sku                 = "Standard"
  # Not bound to any ipConfiguration -> isnull(properties.ipConfiguration)
}

# 3. NIC with no VM ----------------------------------------------------------
resource "azurerm_virtual_network" "vnet" {
  name                = "orphan-test-vnet"
  location            = azurerm_resource_group.orphan_test.location
  resource_group_name = azurerm_resource_group.orphan_test.name
  address_space       = ["10.0.0.0/16"]
}

resource "azurerm_subnet" "subnet" {
  name                 = "orphan-test-subnet"
  resource_group_name  = azurerm_resource_group.orphan_test.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_network_interface" "orphan_nic" {
  name                = "orphan-test-nic"
  location            = azurerm_resource_group.orphan_test.location
  resource_group_name = azurerm_resource_group.orphan_test.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
  }
  # Never attached to a VM -> isnull(properties.virtualMachine)
}

output "next_step" {
  value = "Now run:  az orphan scan --type all --estimate-cost"
}
