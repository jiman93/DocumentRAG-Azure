@description('Name of the Container Apps managed environment')
param environmentName string

@description('Azure region for the managed environment')
param location string

@description('Optional tags to apply to the environment')
param tags object = {}

resource managedEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: environmentName
  location: location
  tags: tags
  properties: {
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
  }
}

output environmentId string = managedEnvironment.id

