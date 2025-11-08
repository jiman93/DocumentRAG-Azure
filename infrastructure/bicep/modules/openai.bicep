@description('Name of the Azure OpenAI resource')
param openAiAccountName string

@description('Azure region for the OpenAI resource')
param location string

@description('SKU tier for the OpenAI resource')
@allowed([
  'S0'
])
param skuName string = 'S0'

@description('Optional network mode setting. Set to "Open" for public network access or "Disabled" to restrict.')
@allowed([
  'Open'
  'Disabled'
])
param networkAclsDefaultAction string = 'Open'

@description('Optional tags to apply to the resource')
param tags object = {}

resource openAiAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: openAiAccountName
  location: location
  sku: {
    name: skuName
  }
  kind: 'OpenAI'
  tags: tags
  properties: {
    networkAcls: {
      defaultAction: networkAclsDefaultAction
    }
    publicNetworkAccess: networkAclsDefaultAction == 'Open' ? 'Enabled' : 'Disabled'
  }
}

output openAiAccountId string = openAiAccount.id
output openAiEndpoint string = openAiAccount.properties.endpoint

