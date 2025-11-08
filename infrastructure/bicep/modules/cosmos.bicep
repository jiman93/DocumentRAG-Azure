@description('Name of the Cosmos DB account')
param accountName string

@description('Azure region for the Cosmos DB account')
param location string

@description('Optional secondary write region (leave empty for single-region)')
param secondaryLocation string = ''

@description('Cosmos DB API kind')
@allowed([
  'GlobalDocumentDB'
])
param kind string = 'GlobalDocumentDB'

@description('Consistency level')
@allowed([
  'Strong'
  'BoundedStaleness'
  'Session'
  'Eventual'
  'ConsistentPrefix'
])
param consistencyLevel string = 'Session'

@description('Enable Free Tier (true/false)')
param enableFreeTier bool = true

@description('Name of the database to create')
param databaseName string

@description('Name of the documents container')
param documentsContainerName string = 'documents'

@description('Partition key path for the documents container')
param documentsPartitionKey string = '/document_id'

@description('Name of the conversations container')
param conversationsContainerName string = 'conversations'

@description('Partition key path for the conversations container')
param conversationsPartitionKey string = '/conversation_id'

@description('Optional tags to apply to the account')
param tags object = {}

var secondaryLocationConfig = empty(secondaryLocation) ? [] : [
  {
    locationName: secondaryLocation
    failoverPriority: 1
    isZoneRedundant: false
  }
]

resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: accountName
  location: location
  kind: kind
  tags: tags
  properties: {
    databaseAccountOfferType: 'Standard'
    enableFreeTier: enableFreeTier
    consistencyPolicy: {
      defaultConsistencyLevel: consistencyLevel
    }
    locations: concat([
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ], secondaryLocationConfig)
  }
}

resource cosmosDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-05-15' = {
  name: '${cosmosAccount.name}/${databaseName}'
  properties: {
    resource: {
      id: databaseName
    }
  }
  dependsOn: [
    cosmosAccount
  ]
}

resource documentsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = {
  name: '${cosmosDatabase.name}/${documentsContainerName}'
  properties: {
    resource: {
      id: documentsContainerName
      partitionKey: {
        paths: [
          documentsPartitionKey
        ]
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        automatic: true
      }
    }
  }
  dependsOn: [
    cosmosDatabase
  ]
}

resource conversationsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = {
  name: '${cosmosDatabase.name}/${conversationsContainerName}'
  properties: {
    resource: {
      id: conversationsContainerName
      partitionKey: {
        paths: [
          conversationsPartitionKey
        ]
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        automatic: true
      }
    }
  }
  dependsOn: [
    cosmosDatabase
  ]
}

output cosmosAccountId string = cosmosAccount.id
output cosmosPrimaryConnectionString string = listConnectionStrings(cosmosAccount.id, cosmosAccount.apiVersion).connectionStrings[0].connectionString
output documentsContainerId string = documentsContainer.id
output conversationsContainerId string = conversationsContainer.id

