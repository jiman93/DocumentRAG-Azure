@description('Name of the Azure Container Registry')
param registryName string

@description('Azure region for the registry')
param location string

@description('SKU for the registry')
@allowed([
  'Basic'
  'Standard'
  'Premium'
])
param sku string = 'Basic'

@description('Enable admin user (not recommended for production)')
param adminUserEnabled bool = false

@description('Optional tags to apply to the registry')
param tags object = {}

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: registryName
  location: location
  tags: tags
  sku: {
    name: sku
  }
  properties: {
    adminUserEnabled: adminUserEnabled
    publicNetworkAccess: 'Enabled'
  }
}

output registryId string = registry.id
output loginServer string = registry.properties.loginServer
output adminUsername string = adminUserEnabled ? listCredentials(registry.id, '2023-07-01').username : ''
output adminPassword string = adminUserEnabled ? listCredentials(registry.id, '2023-07-01').passwords[0].value : ''

