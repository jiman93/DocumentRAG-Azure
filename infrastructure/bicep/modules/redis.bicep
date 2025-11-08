@description('Name of the Redis cache')
param redisName string

@description('Azure region for Redis')
param location string

@description('SKU name for Redis cache')
@allowed([
  'Basic'
  'Standard'
  'Premium'
])
param skuName string = 'Basic'

@description('SKU family for Redis cache')
@allowed([
  'C'
  'P'
])
param skuFamily string = 'C'

@description('Capacity for Redis cache (depends on SKU)')
@minValue(0)
@maxValue(6)
param skuCapacity int = 0

@description('Optional tags to apply to the resource')
param tags object = {}

resource redisCache 'Microsoft.Cache/Redis@2023-08-15' = {
  name: redisName
  location: location
  tags: tags
  sku: {
    name: skuName
    family: skuFamily
    capacity: skuCapacity
  }
  properties: {
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
  }
}

output redisId string = redisCache.id
output redisHostName string = redisCache.properties.hostName
output redisPrimaryKey string = listKeys(redisCache.id, redisCache.apiVersion).primaryKey

