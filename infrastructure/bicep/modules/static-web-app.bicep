@description('Name of the Static Web App')
param staticWebAppName string

@description('Azure region for the Static Web App')
param location string

@description('Repository URL (optional) for GitHub Actions integration')
param repositoryUrl string = ''

@description('Branch to use for deployment workflow')
param repositoryBranch string = 'main'

@description('Optional tags to apply to the resource')
param tags object = {}

resource staticWebApp 'Microsoft.Web/staticSites@2023-12-01' = {
  name: staticWebAppName
  location: location
  tags: tags
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    repositoryUrl: empty(repositoryUrl) ? null : repositoryUrl
    branch: repositoryBranch
  }
}

output staticWebAppId string = staticWebApp.id
output staticWebAppDefaultHostname string = staticWebApp.properties.defaultHostname

