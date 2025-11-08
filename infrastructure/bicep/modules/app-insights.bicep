@description('Name of the Application Insights resource')
param appInsightsName string

@description('Azure region for Application Insights')
param location string

@description('Application type')
@allowed([
  'web'
  'other'
])
param applicationType string = 'web'

@description('Optional tags to apply')
param tags object = {}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: applicationType
    Flow_Type: 'Redfield'
    Request_Source: 'rest'
  }
}

output appInsightsId string = appInsights.id
output instrumentationKey string = appInsights.properties.InstrumentationKey
output connectionString string = appInsights.properties.ConnectionString

