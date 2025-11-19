# ECHTE AZURE LOGIN UND DEPLOYMENT - KEINE DEMO
Write-Host "==> AZURE LOGIN UND DEPLOYMENT FÜR AUTONOMOUS ZENITH OPTIMIZER" -ForegroundColor Green

# Echter Azure Login mit interaktivem Login
az login --use-device-code

# Überprüfe Subscription
az account show --query '{Name:name, ID:id, SubscriptionId:id}' -o table

# Echte Cognitive Services Account Konfiguration
$ResourceGroup  = "rg-azo-production"
$Location       = "switzerlandnorth"
$AccountName    = "azo-openai-prod"
$DeploymentName = "gpt4-turbo-prod"
$SubscriptionId = (az account show --query id -o tsv)

# Erstelle Resource Group falls nicht vorhanden
az group create --name $ResourceGroup --location $Location --subscription $SubscriptionId

# Echte Cognitive Services Account bereitstellen
az cognitiveservices account create `
  --name $AccountName `
  --resource-group $ResourceGroup `
  --kind OpenAI `
  --sku S0 `
  --location $Location

# Echte API Keys regenerieren
az cognitiveservices account keys regenerate `
  --name $AccountName `
  --resource-group $ResourceGroup `
  --key-name key1

$BicepTemplate = @"
{
  "`$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "accountName": {
      "type": "string",
      "defaultValue": "$AccountName"
    },
    "location": {
      "type": "string",
      "defaultValue": "$Location"
    }
  },
  "resources": [
    {
      "type": "Microsoft.CognitiveServices/accounts",
      "apiVersion": "2021-10-01",
      "name": "[parameters('accountName')]",
      "location": "[parameters('location')]",
      "sku": {
        "name": "S0"
      },
      "kind": "OpenAI",
      "properties": {
        "customSubDomainName": "$AccountName",
        "networkAcls": {
          "defaultAction": "Allow"
        }
