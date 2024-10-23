# Step 4: Prompt for API Key and Endpoint Input

$vaultName = "LabVault123"  # You can change this name if you'd like


# Prompt for API Key
$api_key = Read-Host -Prompt "Enter your API key"

# Prompt for Computer Vision Endpoint
$endpoint = Read-Host -Prompt "Enter your Computer Vision endpoint"

# Step 5: Add Secrets to Key Vault
# Add the API key as a secret to Key Vault
az keyvault secret set --vault-name $vaultName --name "MySecretApiKey" --value $api_key

# Add the Computer Vision endpoint as another secret to Key Vault
az keyvault secret set --vault-name $vaultName --name "ComputerVisionEndpoint" --value $endpoint

# Confirmation Output
Write-Host "Secrets successfully added to Key Vault: $vaultName"
