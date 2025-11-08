@description('Name of the Key Vault')
param keyVaultName string

@description('Azure region for the Key Vault')
param location string

@description('Tenant ID that owns the vault')
param tenantId string

@description('Access policies to assign')
param accessPolicies array = []

@description('SKU for Key Vault')
@allowed([
  'standard'
  'premium'
])
param skuName string = 'standard'

@description('Optional tags to apply to the vault')
param tags object = {}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    tenantId: tenantId
    enableRbacAuthorization: false
    sku: {
      family: 'A'
      name: toUpper(skuName)
    }
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: true
    accessPolicies: accessPolicies
    publicNetworkAccess: 'Enabled'
  }
}

output keyVaultId string = keyVault.id
output keyVaultUri string = keyVault.properties.vaultUri

