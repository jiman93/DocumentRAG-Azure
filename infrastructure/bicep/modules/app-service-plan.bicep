@description('Name of the App Service plan')
param planName string

@description('Azure region for the App Service plan')
param location string

@description('SKU tier for the plan')
@allowed([
  'Free'
  'Shared'
  'Basic'
  'Standard'
  'Premium'
  'PremiumV2'
  'PremiumV3'
  'Isolated'
  'IsolatedV2'
])
param skuTier string = 'PremiumV3'

@description('SKU size for the plan')
param skuSize string = 'P1v3'

@description('Worker count')
@minValue(1)
@maxValue(10)
param workerCount int = 1

@description('True to use Linux workers')
param linuxWorkers bool = true

@description('Optional tags to apply to the plan')
param tags object = {}

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  tags: tags
  sku: {
    name: skuSize
    tier: skuTier
    capacity: workerCount
  }
  properties: {
    reserved: linuxWorkers
    zoneRedundant: false
  }
}

output planId string = plan.id

