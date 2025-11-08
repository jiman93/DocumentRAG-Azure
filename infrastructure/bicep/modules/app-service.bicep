@description('Name of the App Service')
param siteName string

@description('Azure region for the App Service')
param location string

@description('Resource ID of the App Service plan')
param planId string

@description('Key/value pairs for application settings')
param appSettings object = {}

@description('Connection string settings (name -> object with type & value)')
param connectionStrings object = {}

@description('Optional tags to apply to the site')
param tags object = {}

var appSettingsArray = [
  for key in union([], keys(appSettings)): {
    name: key
    value: string(appSettings[key])
  }
]

var connectionStringsArray = [
  for key in union([], keys(connectionStrings)): {
    name: key
    connectionString: string(connectionStrings[key].value)
    type: string(connectionStrings[key].type)
  }
]

resource site 'Microsoft.Web/sites@2023-12-01' = {
  name: siteName
  location: location
  tags: tags
  properties: {
    serverFarmId: planId
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.12'
      appSettings: appSettingsArray
      connectionStrings: connectionStringsArray
      ftpsState: 'Disabled'
    }
  }
}

output siteId string = site.id
output defaultHostname string = site.properties.defaultHostName

