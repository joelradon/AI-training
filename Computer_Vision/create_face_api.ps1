# Step 1: Prompt for Resource Group (with default "radon-ai")
$resource_group = Read-Host -Prompt "Enter the resource group name (default: radon-ai)"
if (-not $resource_group) { $resource_group = "radon-ai" }

# Step 2: Prompt for Key Vault Name (with default "LabVault123")
$key_vault_name = Read-Host -Prompt "Enter the Key Vault name (default: LabVault123)"
if (-not $key_vault_name) { $key_vault_name = "LabVault123" }

# Step 3: Create the Resource Group (if it doesn't already exist)
az group create --name $resource_group --location "eastus"

# Step 4: Create the Face API resource using Free Tier (F0)
az cognitiveservices account create `
  --name "FaceAPIResource" `
  --resource-group $resource_group `
  --kind "Face" `
  --sku "F0" `
  --location "eastus" `
  --yes `
  --api-properties "Kind=Face"

# Step 5: Retrieve the Face API Key
$FACE_API_KEY = az cognitiveservices account keys list `
  --name "FaceAPIResource" `
  --resource-group $resource_group `
  --query "key1" -o tsv

# Step 6: Retrieve the Face API Endpoint
$FACE_API_ENDPOINT = az cognitiveservices account show `
  --name "FaceAPIResource" `
  --resource-group $resource_group `
  --query "properties.endpoint" -o tsv

# Step 7: Store the Face API Key in the Key Vault
az keyvault secret set `
  --vault-name $key_vault_name `
  --name "FaceAPIKey" `
  --value $FACE_API_KEY

# Step 8: Store the Face API Endpoint in the Key Vault
az keyvault secret set `
  --vault-name $key_vault_name `
  --name "FaceAPIEndpoint" `
  --value $FACE_API_ENDPOINT

# Step 9: Output confirmation
Write-Host "Face API Key and Endpoint have been successfully stored in Key Vault: $key_vault_name"
