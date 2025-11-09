targetScope = 'resourceGroup'

@description('Name of the budget resource')
param budgetName string

@description('Monthly budget amount in USD')
param amount int = 20

@description('Email addresses to notify when thresholds are hit')
param contactEmails array

@description('Budget start date in ISO 8601 format (e.g. 2025-11-01T00:00:00Z)')
param startDate string

@description('Budget end date in ISO 8601 format')
param endDate string

resource budget 'Microsoft.Consumption/budgets@2023-05-01' = {
  name: budgetName
  properties: {
    amount: amount
    category: 'Cost'
    timeGrain: 'Monthly'
    timePeriod: {
      startDate: startDate
      endDate: endDate
    }
    notifications: {
      seventyFivePercent: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 75
        contactEmails: contactEmails
      }
      hundredPercent: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 100
        contactEmails: contactEmails
        contactRoles: [
          'Contributor'
        ]
      }
    }
  }
}

