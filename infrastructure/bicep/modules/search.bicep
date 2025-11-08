@description('Name of the Azure AI Search service')
param searchServiceName string

@description('Azure region for the Search service')
param location string

@description('SKU for the Search service')
@allowed([
  'basic'
  'standard'
  'standard2'
  'standard3'
  'storage_optimized_l1'
  'storage_optimized_l2'
])
param skuName string = 'standard'

@description('Replica count (1-12)')
@minValue(1)
@maxValue(12)
param replicaCount int = 1

@description('Partition count (1-12)')
@minValue(1)
@maxValue(12)
param partitionCount int = 1

@description('Optional tags to apply to the resource')
param tags object = {}

resource searchService 'Microsoft.Search/searchServices@2023-11-01' = {
  name: searchServiceName
  location: location
  sku: {
    name: skuName
  }
  tags: tags
  properties: {
    replicas: replicaCount
    partitions: partitionCount
    hostingMode: 'default'
  }
}

output searchServiceId string = searchService.id
output searchServiceEndpoint string = 'https://${searchService.name}.search.windows.net'

