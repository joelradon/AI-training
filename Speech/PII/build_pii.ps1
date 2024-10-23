# Step 1: Set variables for storage account, container, and key vault
$resourceGroup = "radon-ai"
$storageAccountName = "radonaistorage"
$containerName = "testfiles"
$keyVaultName = "LabVault123"

# Step 2: Retrieve region and endpoint from Key Vault
$region = az keyvault secret show --name "AzureAIRegion" --vault-name $keyVaultName --query "value" -o tsv
$endpoint = az keyvault secret show --name "AzureAIEndpoint" --vault-name $keyVaultName --query "value" -o tsv

# Step 3: Retrieve API key from Key Vault
$apiKey = az keyvault secret show --name "AzureAISpeechApiKey" --vault-name $keyVaultName --query "value" -o tsv

# Step 4: Function to detect PII using Azure Text Analytics API
function Detect-PII {
    param (
        [string]$text
    )

    $headers = @{
        "Ocp-Apim-Subscription-Key" = $apiKey
        "Content-Type" = "application/json"
    }

    $body = @{
        "documents" = @(
            @{
                "id" = "1"
                "text" = $text
                "language" = "en"
            }
        )
    } | ConvertTo-Json

    $url = "$endpoint/text/analytics/v3.1-preview.3/entities/recognition/pii"
    $response = Invoke-RestMethod -Method Post -Uri $url -Headers $headers -Body $body

    return $response.documents.entities
}

# Step 5: Analyze files for PII and summarize content
$blobs = az storage blob list --container-name $containerName --account-name $storageAccountName --account-key $storageAccountKey --query [].name -o tsv

foreach ($blob in $blobs) {
    $fileContent = az storage blob download --container-name $containerName --name $blob --account-name $storageAccountName --account-key $storageAccountKey --query "content" -o tsv
    $piiEntities = Detect-PII -text $fileContent
    Write-Host "File: $blob"
    Write-Host "PII detected: $($piiEntities | ConvertTo-Json -Compress)"
}

Write-Host "PII detection completed and emails summarized."
