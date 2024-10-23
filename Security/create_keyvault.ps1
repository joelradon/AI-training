# Step 1: Prompt for Subscription ID
$subscriptionId = Read-Host -Prompt "Enter your Azure Subscription ID"

# Step 2: Create Azure Key Vault
$vaultName = "LabVault123"  # You can change this name if you'd like
$resourceGroupName = "radon-ai"
$location = "eastus"

# Set the subscription for the current session
az account set --subscription $subscriptionId

# Create the Key Vault
az keyvault create --name $vaultName --resource-group $resourceGroupName --location $location

# Step 3: Assign RBAC Role to Current User (Key Vault Secrets Officer and Key Vault Secrets User)

# Get the Object ID of the current user (or you can specify a service principal)
$currentUserObjectId = az ad signed-in-user show --query objectId -o tsv

# Assign 'Key Vault Secrets Officer' role to the current user (for secret management)
az role assignment create --role "Key Vault Secrets Officer" --assignee $currentUserObjectId --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.KeyVault/vaults/$vaultName"

# Assign 'Key Vault Secrets User' role to the current user (for secret viewing)
az role assignment create --role "Key Vault Secrets User" --assignee $currentUserObjectId --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.KeyVault/vaults/$vaultName"

# Output a message to wait for 15 minutes before proceeding to the next script
Write-Host "Roles assigned. Please wait at least 15 minutes for role propagation before running the next script."
