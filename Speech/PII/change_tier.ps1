# Step 1: Prompt for input with defaults
$resourceGroup = Read-Host -Prompt "Enter the resource group name (default: 'radon-ai')"
if (-not $resourceGroup) { $resourceGroup = "radon-ai" }

$textAnalyticsName = Read-Host -Prompt "Enter the Text Analytics service name (default: 'TextAnalytics1234')"
if (-not $textAnalyticsName) { $textAnalyticsName = "TextAnalytics1234" }

# Step 2: Update the Text Analytics service pricing tier to S0
az cognitiveservices account update `
  --name $textAnalyticsName `
  --resource-group $resourceGroup `
  --sku S0

# Step 3: Confirm the pricing tier has been updated
az cognitiveservices account show `
  --name $textAnalyticsName `
  --resource-group $resourceGroup `
  --query "sku.name"
