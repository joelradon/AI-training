# Step 1: Set variables for resource group, location, and key vault with defaults
$resourceGroup = Read-Host -Prompt "Enter the resource group name (default: 'radon-ai')" 
if (-not $resourceGroup) { $resourceGroup = "radon-ai" }

$location = Read-Host -Prompt "Enter the location (default: 'eastus')" 
if (-not $location) { $location = "eastus" }

$keyVaultName = Read-Host -Prompt "Enter the Key Vault name (default: 'LabVault123')" 
if (-not $keyVaultName) { $keyVaultName = "LabVault123" }

$textAnalyticsResourceName = "TextAnalytics" + (Get-Random -Maximum 10000)  # Unique name for the Text Analytics resource

# Step 2: Create the Text Analytics resource in Azure
Write-Host "Creating Text Analytics resource: $textAnalyticsResourceName in resource group: $resourceGroup"
az cognitiveservices account create `
  --name $textAnalyticsResourceName `
  --resource-group $resourceGroup `
  --kind TextAnalytics `
  --sku F0 `
  --location $location `
  --yes

# Step 3: Retrieve the API key and endpoint from the Text Analytics resource
$apiKey = az cognitiveservices account keys list --resource-group $resourceGroup --name $textAnalyticsResourceName --query '[0].value' -o tsv
$endpoint = az cognitiveservices account show --name $textAnalyticsResourceName --resource-group $resourceGroup --query "properties.endpoint" -o tsv

# Step 4: Store the API key and endpoint in Azure Key Vault
Write-Host "Storing API key and endpoint in Key Vault: $keyVaultName"
az keyvault secret set --vault-name $keyVaultName --name "AzureAITextAnalyticsApiKey" --value $apiKey
az keyvault secret set --vault-name $keyVaultName --name "AzureAITextAnalyticsEndpoint" --value $endpoint

# Step 5: Output confirmation
Write-Host "Text Analytics resource created: $textAnalyticsResourceName"
Write-Host "API key and endpoint have been stored in Key Vault: $keyVaultName"
