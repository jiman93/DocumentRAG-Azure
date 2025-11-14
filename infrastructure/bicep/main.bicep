@description('Base prefix for all resource names (alphanumeric, short)')
param resourcePrefix string = 'docrag'

@description('Deployment environment identifier (e.g. dev, stg, prod)')
param environment string = 'dev'

@description('Azure region for deployment')
param location string = 'eastus'

@description('Azure region for the Azure OpenAI resource (defaults to deployment location)')
param openAiLocation string = location

@description('Azure region for the Static Web App (must be in allowed list)')
@allowed([
  'westus2'
  'centralus'
  'eastus2'
  'westeurope'
  'eastasia'
])
param staticWebAppLocation string = 'eastus2'

@description('Container image reference for the .NET gateway. Use a public image until you push to ACR.')
param gatewayContainerImage string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

@description('Container image reference for the Python RAG API. Use a public image until you push to ACR.')
param pythonContainerImage string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

@description('Repository URL for the Static Web App (required if deployStaticWebApp is true)')
param staticWebAppRepositoryUrl string = ''

@description('Repository branch for the Static Web App')
param staticWebAppRepositoryBranch string = 'main'

@description('Tenant ID for Key Vault access configuration')
param tenantId string

@description('Toggle to deploy Redis cache')
param deployRedis bool = false

@description('Toggle to deploy Static Web App')
param deployStaticWebApp bool = false

# Search resources are temporarily disabled from IaC to control costs.
# @description('Toggle to deploy Azure AI Search service')
# param deploySearch bool = false

@description('Toggle to deploy a Cost Management budget')
param deployBudget bool = false

@description('Toggle to deploy the Python RAG API App Service')
param deployPythonApi bool = false

@description('Monthly budget amount in USD')
param budgetAmount int = 20

@description('Budget notification email recipients')
param budgetContactEmails array = []

@description('Budget start date (ISO 8601). Defaults to now.')
param budgetStartDate string = utcNow()

@description('Budget end date (ISO 8601). Defaults to one year after start')
param budgetEndDate string = dateTimeAdd(budgetStartDate, 'P1Y')

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
var containerRegistryName = take('${normalizedPrefix}${uniqueSuffix}acr', 50)
var containerAppEnvironmentName = '${normalizedPrefix}-${environment}-cae'
var gatewayContainerAppName = '${normalizedPrefix}-${environment}-gateway'
var pythonContainerAppName = '${normalizedPrefix}-${environment}-rag'
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
    location: openAiLocation
    tags: globalTags
  }
}

// Azure Cognitive Search deployment disabled to control cost footprint.
var searchEndpoint = ''

var pythonContainerEnvVars = [
  {
    name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
    value: appInsights.outputs.instrumentationKey
  }
  {
    name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
    value: appInsights.outputs.connectionString
  }
  {
    name: 'AZURE_OPENAI_ENDPOINT'
    value: openAi.outputs.openAiEndpoint
  }
  {
    name: 'AZURE_OPENAI_RESOURCE_ID'
    value: openAi.outputs.openAiAccountId
  }
  {
    name: 'AZURE_SEARCH_ENDPOINT'
    value: searchEndpoint
  }
  {
    name: 'COSMOS_ACCOUNT_ID'
    value: cosmos.outputs.cosmosAccountId
  }
  {
    name: 'STORAGE_ACCOUNT_ID'
    value: storage.outputs.storageAccountId
  }
  {
    name: 'KEY_VAULT_URI'
    value: keyVault.outputs.keyVaultUri
  }
  {
    name: 'PORT'
    value: '8000'
  }
]

module cosmos 'modules/cosmos.bicep' = {
  name: 'cosmosDb'
  params: {
    accountName: cosmosAccountName
    location: location
    enableFreeTier: false
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

module containerRegistry 'modules/acr.bicep' = {
  name: 'containerRegistry'
  params: {
    registryName: containerRegistryName
    location: location
    tags: globalTags
    adminUserEnabled: true
  }
}

module containerAppEnvironment 'modules/container-app-env.bicep' = {
  name: 'containerAppEnvironment'
  params: {
    environmentName: containerAppEnvironmentName
    location: location
    tags: globalTags
  }
}

resource containerRegistryResource 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: containerRegistryName
}

var containerRegistryUsername = containerRegistry.outputs.adminUsername
var containerRegistryPassword = containerRegistry.outputs.adminPassword
var containerRegistryLoginServer = containerRegistry.outputs.loginServer
var containerRegistryLoginServerLower = toLower(containerRegistryLoginServer)

var gatewayImageLower = toLower(gatewayContainerImage)
var pythonImageLower = toLower(pythonContainerImage)
var gatewayImageUsesRegistry = !empty(containerRegistryLoginServer) && startsWith(gatewayImageLower, containerRegistryLoginServerLower)
var pythonImageUsesRegistry = !empty(containerRegistryLoginServer) && startsWith(pythonImageLower, containerRegistryLoginServerLower)

module pythonContainerApp 'modules/container-app.bicep' = if (deployPythonApi) {
  name: 'pythonContainerApp'
  params: {
    containerAppName: pythonContainerAppName
    location: location
    environmentId: containerAppEnvironment.outputs.environmentId
    image: pythonContainerImage
    registryServer: pythonImageUsesRegistry ? containerRegistryLoginServer : ''
    registryUsername: pythonImageUsesRegistry ? containerRegistryUsername : ''
    registryPassword: pythonImageUsesRegistry ? containerRegistryPassword : ''
    environmentVariables: pythonContainerEnvVars
    ingressTargetPort: 8000
    containerName: 'python-rag'
    tags: globalTags
  }
  dependsOn: [
    containerRegistry
    containerAppEnvironment
    appInsights
    openAi
    cosmos
    storage
    keyVault
  ]
}

var pythonApiUrl = deployPythonApi ? 'https://${pythonContainerFqdn}' : 'http://localhost:8000'

var gatewayContainerEnvVars = [
  {
    name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
    value: appInsights.outputs.instrumentationKey
  }
  {
    name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
    value: appInsights.outputs.connectionString
  }
  {
    name: 'AZURE_OPENAI_ENDPOINT'
    value: openAi.outputs.openAiEndpoint
  }
  {
    name: 'AZURE_OPENAI_RESOURCE_ID'
    value: openAi.outputs.openAiAccountId
  }
  {
    name: 'AZURE_SEARCH_ENDPOINT'
    value: searchEndpoint
  }
  {
    name: 'COSMOS_ACCOUNT_ID'
    value: cosmos.outputs.cosmosAccountId
  }
  {
    name: 'STORAGE_ACCOUNT_ID'
    value: storage.outputs.storageAccountId
  }
  {
    name: 'KEY_VAULT_URI'
    value: keyVault.outputs.keyVaultUri
  }
  {
    name: 'ASPNETCORE_URLS'
    value: 'http://+:8080'
  }
  {
    name: 'Gateway__PythonRagApiUrl'
    value: pythonApiUrl
  }
  {
    name: 'HealthChecksUI__HealthChecks__0__Uri'
    value: 'http://localhost:8080/health'
  }
  {
    name: 'HealthChecksUI__HealthChecks__1__Uri'
    value: '${pythonApiUrl}/health'
  }
]

module gatewayContainerApp 'modules/container-app.bicep' = {
  name: 'gatewayContainerApp'
  params: {
    containerAppName: gatewayContainerAppName
    location: location
    environmentId: containerAppEnvironment.outputs.environmentId
    image: gatewayContainerImage
    registryServer: gatewayImageUsesRegistry ? containerRegistryLoginServer : ''
    registryUsername: gatewayImageUsesRegistry ? containerRegistryUsername : ''
    registryPassword: gatewayImageUsesRegistry ? containerRegistryPassword : ''
    environmentVariables: gatewayContainerEnvVars
    ingressTargetPort: 8080
    containerName: 'gateway-api'
    tags: globalTags
  }
  dependsOn: [
    containerRegistry
    containerAppEnvironment
    appInsights
    openAi
    cosmos
    storage
    keyVault
  ]
}

resource pythonAcrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (deployPythonApi) {
  name: guid(containerRegistryName, pythonContainerAppName, 'acrpull')
  scope: containerRegistryResource
  properties: {
    principalId: pythonContainerApp.outputs.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalType: 'ServicePrincipal'
  }
  dependsOn: [
    pythonContainerApp
  ]
}

resource gatewayAcrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(containerRegistryName, gatewayContainerAppName, 'acrpull')
  scope: containerRegistryResource
  properties: {
    principalId: gatewayContainerApp.outputs.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalType: 'ServicePrincipal'
  }
  dependsOn: [
    gatewayContainerApp
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

var pythonContainerFqdn = deployPythonApi ? '${pythonContainerAppName}.${location}.azurecontainerapps.io' : ''
var gatewayContainerFqdn = '${gatewayContainerAppName}.${location}.azurecontainerapps.io'
var gatewayApiUrl = 'https://${gatewayContainerFqdn}'

module staticWebApp 'modules/static-web-app.bicep' = if (deployStaticWebApp && !empty(staticWebAppRepositoryUrl)) {
  name: 'staticWebApp'
  params: {
    staticWebAppName: staticWebAppName
    location: staticWebAppLocation
    repositoryUrl: staticWebAppRepositoryUrl
    repositoryBranch: staticWebAppRepositoryBranch
    tags: globalTags
  }
}

var staticWebAppHostname = deployStaticWebApp && !empty(staticWebAppRepositoryUrl) ? staticWebApp.outputs.staticWebAppDefaultHostname : ''

module budget 'modules/budget.bicep' = if (deployBudget && length(budgetContactEmails) > 0) {
  name: 'costBudget'
  scope: resourceGroup()
  params: {
    budgetName: '${normalizedPrefix}-${environment}-budget'
    amount: budgetAmount
    contactEmails: budgetContactEmails
    startDate: budgetStartDate
    endDate: budgetEndDate
  }
}

output storageAccountName string = storageAccountName
output openAiResourceId string = openAi.outputs.openAiAccountId
output searchServiceEndpoint string = searchEndpoint
output cosmosConnectionString string = cosmos.outputs.cosmosPrimaryConnectionString
output pythonApiUrl string = pythonApiUrl
output keyVaultUri string = keyVault.outputs.keyVaultUri
output appInsightsConnectionString string = appInsights.outputs.connectionString
output redisHost string = deployRedis ? redis.outputs.redisHostName : ''
output staticWebAppHostname string = staticWebAppHostname
output containerRegistryLoginServer string = deployPythonApi ? containerRegistry.outputs.loginServer : ''
output pythonContainerAppFqdn string = pythonContainerFqdn
output gatewayContainerAppFqdn string = gatewayContainerFqdn
output gatewayApiUrl string = gatewayApiUrl

