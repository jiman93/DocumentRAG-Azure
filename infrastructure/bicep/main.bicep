@description('Base prefix for all resource names (alphanumeric, short)')
param resourcePrefix string = 'docrag'

@description('Deployment environment identifier (e.g. dev, stg, prod)')
param environment string = 'dev'

@description('Azure region for deployment')
param location string = 'eastus'

@description('Tenant ID for Key Vault access configuration')
param tenantId string

@description('Toggle to deploy Redis cache')
param deployRedis bool = false

@description('Toggle to deploy Static Web App')
param deployStaticWebApp bool = false

@description('Optional tags to apply to all resources')
param tags object = {}

var normalizedPrefix = toLower(replace(resourcePrefix, '-', ''))
var uniqueSuffix = toLower(take(uniqueString(subscription().id, environment, location), 6))
var globalTags = union(tags, {
  environment: environment
  workload: 'document-rag'
})

// Name helpers
var storageAccountName = take('${normalizedPrefix}${uniqueSuffix}st', 24)
var openAiName = '${normalizedPrefix}-${environment}-openai'
var searchServiceName = '${normalizedPrefix}-${environment}-search'
var cosmosAccountName = '${normalizedPrefix}-${environment}-cosmos'
var redisName = '${normalizedPrefix}-${environment}-redis'
var appServicePlanName = '${normalizedPrefix}-${environment}-plan'
var appServiceName = '${normalizedPrefix}-${environment}-api'
var staticWebAppName = '${normalizedPrefix}-${environment}-swa'
var keyVaultName = '${normalizedPrefix}-${environment}-kv'
var appInsightsName = '${normalizedPrefix}-${environment}-appi'
var cosmosDatabaseName = 'ragdata'

module storage 'modules/storage.bicep' = {
  name: 'storageAccount'
  params: {
    storageAccountName: storageAccountName
    location: location
    tags: globalTags
  }
}

module openAi 'modules/openai.bicep' = {
  name: 'openAi'
  params: {
    openAiAccountName: openAiName
    location: location
    tags: globalTags
  }
}

module search 'modules/search.bicep' = {
  name: 'searchService'
  params: {
    searchServiceName: searchServiceName
    location: location
    tags: globalTags
  }
}

module cosmos 'modules/cosmos.bicep' = {
  name: 'cosmosDb'
  params: {
    accountName: cosmosAccountName
    location: location
    databaseName: cosmosDatabaseName
    documentsContainerName: 'documents'
    conversationsContainerName: 'conversations'
    tags: globalTags
  }
}

module appInsights 'modules/app-insights.bicep' = {
  name: 'appInsights'
  params: {
    appInsightsName: appInsightsName
    location: location
    tags: globalTags
  }
}

module keyVault 'modules/key-vault.bicep' = {
  name: 'keyVault'
  params: {
    keyVaultName: keyVaultName
    location: location
    tenantId: tenantId
    tags: globalTags
  }
}

module plan 'modules/app-service-plan.bicep' = {
  name: 'appServicePlan'
  params: {
    planName: appServicePlanName
    location: location
    tags: globalTags
  }
}

module appService 'modules/app-service.bicep' = {
  name: 'appService'
  params: {
    siteName: appServiceName
    location: location
    planId: plan.outputs.planId
    tags: globalTags
    appSettings: {
      'APPINSIGHTS_INSTRUMENTATIONKEY': appInsights.outputs.instrumentationKey
      'APPLICATIONINSIGHTS_CONNECTION_STRING': appInsights.outputs.connectionString
      'AZURE_OPENAI_ENDPOINT': openAi.outputs.openAiEndpoint
      'AZURE_OPENAI_RESOURCE_ID': openAi.outputs.openAiAccountId
      'AZURE_SEARCH_ENDPOINT': search.outputs.searchServiceEndpoint
      'COSMOS_ACCOUNT_ID': cosmos.outputs.cosmosAccountId
      'STORAGE_ACCOUNT_ID': storage.outputs.storageAccountId
      'KEY_VAULT_URI': keyVault.outputs.keyVaultUri
    }
  }
  dependsOn: [
    plan
    appInsights
    openAi
    search
    cosmos
    storage
    keyVault
  ]
}

module redis 'modules/redis.bicep' = if (deployRedis) {
  name: 'redis'
  params: {
    redisName: redisName
    location: location
    tags: globalTags
  }
}

module staticWebApp 'modules/static-web-app.bicep' = if (deployStaticWebApp) {
  name: 'staticWebApp'
  params: {
    staticWebAppName: staticWebAppName
    location: location
    tags: globalTags
  }
}

output storageAccountName string = storageAccountName
output openAiResourceId string = openAi.outputs.openAiAccountId
output searchServiceEndpoint string = search.outputs.searchServiceEndpoint
output cosmosConnectionString string = cosmos.outputs.cosmosPrimaryConnectionString
output appServiceUrl string = 'https://${appServiceName}.azurewebsites.net'
output keyVaultUri string = keyVault.outputs.keyVaultUri
output appInsightsConnectionString string = appInsights.outputs.connectionString
output redisHost string = deployRedis ? redis.outputs.redisHostName : ''

