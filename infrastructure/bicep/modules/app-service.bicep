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
  for setting in items(appSettings): {
    name: setting.key
    value: string(setting.value)
  }
]

var connectionStringsArray = [
  for setting in items(connectionStrings): {
    name: setting.key
    connectionString: string(setting.value.value)
    type: string(setting.value.type)
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

