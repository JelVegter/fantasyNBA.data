# Configure the Azure provider
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 2.65"
    }
  }

  required_version = ">= 1.1.0"
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg1" {
  name     = "fantasy-nba"
  location = "westeurope"
}

resource "azurerm_storage_account" "sa1" {
  name                     = "fantasynba"
  resource_group_name      = azurerm_resource_group.rg1.name
  location                 = azurerm_resource_group.rg1.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "sc1" {
  name                  = "gamesplayed"
  storage_account_name  = azurerm_storage_account.sa1.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "sc2" {
  name                  = "playerstats"
  storage_account_name  = azurerm_storage_account.sa1.name
  container_access_type = "private"
}