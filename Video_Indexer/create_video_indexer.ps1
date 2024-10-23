# Step 1: Set variables for resource group, region, and key vault name with prompts and defaults
$resourceGroup = Read-Host -Prompt "Enter the resource group name (default: 'radon-ai')" 
if (-not $resourceGroup) { $resourceGroup = "radon-ai" }

$location = Read-Host -Prompt "Enter the region (default: 'eastus')"
if (-not $location) { $location = "eastus" }

$keyVaultName = Read-Host -Prompt "Enter the Key Vault name (default: 'LabVault123')"
if (-not $keyVaultName) { $keyVaultName = "LabVault123" }

# Step 2: Create the resource group (if it doesn't exist)
az group create --name $resourceGroup --location $location

# Step 3: Create the Azure AI Video Indexer (Free Tier F0)
$videoIndexerName = "VideoIndexerResource"  # Adjust this name as needed
az cognitiveservices account create --name $videoIndexerName --resource-group $resourceGroup --kind "VideoIndexer" --sku F0 --location $location --yes --api-properties "Kind=VideoIndexer"

# Step 4: Retrieve the API Key and Account ID for the Video Indexer
$apiKey = az cognitiveservices account keys list --name $videoIndexerName --resource-group $resourceGroup --query "key1" -o tsv

$accountId = az cognitiveservices account show --name $videoIndexerName --resource-group $resourceGroup --query "id" -o tsv

# Step 5: Store the API Key and Account ID in the Key Vault
az keyvault secret set --vault-name $keyVaultName --name "VideoIndexerApiKey" --value $apiKey

az keyvault secret set --vault-name $keyVaultName --name "VideoIndexerAccountId" --value $accountId

# Confirmation Output
Write-Host "Video Indexer API Key and Account ID have been successfully stored in Key Vault: $keyVaultName"
