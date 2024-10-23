# Step 1: Set variables for resource group and storage account
$resourceGroup = Read-Host -Prompt "Enter the resource group name (default: 'radon-ai')" 
if (-not $resourceGroup) { $resourceGroup = "radon-ai" }

$location = "eastus"  # You can change this to your preferred region
$storageAccountName = "radonaistorage"  # Default storage account name
$containerName = "testfiles"

# Step 2: Create the storage account (if it doesn't exist)
az storage account create --name $storageAccountName --resource-group $resourceGroup --location $location --sku Standard_LRS

# Step 3: Get the storage account key and create a Blob container
$storageAccountKey = az storage account keys list --resource-group $resourceGroup --account-name $storageAccountName --query '[0].value' -o tsv
az storage container create --name $containerName --account-name $storageAccountName --account-key $storageAccountKey

Write-Host "Storage account '$storageAccountName' and container '$containerName' created."
