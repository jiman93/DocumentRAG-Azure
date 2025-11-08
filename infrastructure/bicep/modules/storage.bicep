@description('Name of the Storage account')
param storageAccountName string

@description('Azure region for the Storage account')
param location string

@description('SKU for the Storage account')
@allowed([
  'Standard_LRS'
  'Standard_GRS'
  'Standard_RAGRS'
  'Standard_ZRS'
  'Standard_GZRS'
  'Standard_RAGZRS'
])
param skuName string = 'Standard_LRS'

@description('Kind of Storage account to deploy')
@allowed([
  'StorageV2'
  'Storage'
  'BlobStorage'
  'FileStorage'
  'BlockBlobStorage'
])
param kind string = 'StorageV2'

@description('Optional tags to apply to the resource')
param tags object = {}

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  tags: tags
  sku: {
    name: skuName
  }
  kind: kind
  properties: {
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

output storageAccountId string = storageAccount.id
output storagePrimaryEndpoints object = storageAccount.properties.primaryEndpoints

