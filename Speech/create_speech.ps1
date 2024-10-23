# Step 1: Set variables for resource group, region, and key vault with prompts and defaults
$resourceGroup = Read-Host -Prompt "Enter the resource group name (default: 'radon-ai')" 
if (-not $resourceGroup) { $resourceGroup = "radon-ai" }

$location = "eastus"  # You can change this to your preferred region
$keyVaultName = "LabVault123"  # Default Key Vault

# Step 2: Create the resource group (if it doesn't exist)
az group create --name $resourceGroup --location $location

# Step 3: Create Azure AI Speech resource (with automatic naming, in S0 tier)
$speechResourceName = "AI-Speech-" + (Get-Random -Maximum 10000)
az cognitiveservices account create --name $speechResourceName --resource-group $resourceGroup --kind SpeechServices --sku S0 --location $location --yes

# Step 4: Retrieve the API key from the newly created resource
$apiKey = az cognitiveservices account keys list --name $speechResourceName --resource-group $resourceGroup --query "key1" -o tsv

# Step 5: Store the API key in the Key Vault
az keyvault secret set --vault-name $keyVaultName --name "AzureAISpeechApiKey" --value $apiKey

# Step 6: Store the speech resource name in the Key Vault (optional)
az keyvault secret set --vault-name $keyVaultName --name "AzureAISpeechResourceName" --value $speechResourceName

# Confirmation Output
Write-Host "Azure AI Speech service created in S0 tier with the name: $speechResourceName"
Write-Host "API Key stored in Key Vault: $keyVaultName"
