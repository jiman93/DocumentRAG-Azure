@description('Name of the Container App')
param containerAppName string

@description('Azure region for the Container App')
param location string

@description('Resource ID of the Container Apps managed environment')
param environmentId string

@description('Container image (e.g. myregistry.azurecr.io/python-rag:latest)')
param image string

@description('Container registry login server')
param registryServer string

@description('Optional registry username (required if registry password provided)')
param registryUsername string = ''

@description('Optional registry password')
@secure()
param registryPassword string = ''

@description('Secret name to store registry password (if provided)')
param registryPasswordSecretName string = 'acr-password'

@description('Environment variables for the container')
param environmentVariables array = []

@description('Ingress target port')
param ingressTargetPort int = 8000

@description('Name of the container inside the app')
param containerName string = containerAppName

@description('Optional tags to apply to the container app')
param tags object = {}

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: containerAppName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: environmentId
    configuration: {
      ingress: {
        external: true
        targetPort: ingressTargetPort
        transport: 'auto'
      }
      registries: empty(registryUsername) ? [] : [
        {
          server: registryServer
          username: registryUsername
          passwordSecretRef: registryPasswordSecretName
        }
      ]
      secrets: empty(registryPassword) ? [] : [
        {
          name: registryPasswordSecretName
          value: registryPassword
        }
      ]
    }
    template: {
      containers: [
        {
          name: containerName
          image: image
          env: environmentVariables
        }
      ]
    }
  }
}

output containerAppId string = containerApp.id
output principalId string = containerApp.identity.principalId
output ingressFqdn string = containerApp.properties.configuration.ingress.fqdn

