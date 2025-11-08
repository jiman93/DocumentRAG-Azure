@description('Name of the Azure OpenAI resource')
param openAiAccountName string

@description('Azure region for the OpenAI resource')
param location string

@description('SKU tier for the OpenAI resource')
@allowed([
  'S0'
])
param skuName string = 'S0'

@description('Optional network ACL default action. Use "Allow" to enable public access or "Deny" to restrict.')
@allowed([
  'Allow'
  'Deny'
])
param networkAclsDefaultAction string = 'Allow'

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
    publicNetworkAccess: networkAclsDefaultAction == 'Allow' ? 'Enabled' : 'Disabled'
  }
}

output openAiAccountId string = openAiAccount.id
output openAiEndpoint string = openAiAccount.properties.endpoint

