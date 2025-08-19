GET_ASSETS = """ 
query (
  $id: ID!,
  $name: String!,
  $page: Int,
  $limit: Int
) {
  assets(
    companyId: $id
    page: $page
    limit: $limit
    search: {
      name: $name
    }
  ) {
    collection {
      id
      name
      createdAt
      projects(includeAst: true) {
        type
        apiCode
        label
      }
    }

    metadata {
      currentPage
      limitValue
      totalCount
      totalPages
    }
  }
}
"""

GET_ISSUES_STATS = """
query (
  $asset_id: [ID!],
  $company_id: ID!,
  $statuses: [IssueStatusLabel!],
  $end_date: ISO8601DateTime
) {
  issuesStats(
    companyId: $company_id
    filters: {
      assetIds: $asset_id
      statuses: $statuses
      createdAtRange: {
        endDate: $end_date
      }
    }
  ) {
    severities {
      value
      count
    }
  }
}
"""

GET_PROJECTS = """
query (
  $project_code: String!,
  $project_label: String!,
  $company_id: ID!,
  $page: Int,
  $limit: Int
) {
  projects(
    page: $page
    limit: $limit
    params: {
      apiCodeEq: $project_code
      labelEq: $project_label
      scopeIdEq: $company_id
      showHidden: true
      projectTypeLabelEq: "ast"
    }
  ) {
    collection {
      id
      apiCode
      assets {
        id
        name
      }
      company {
        id
        customFeatures
      }
    }
    metadata {
      currentPage
      limitValue
      totalCount
      totalPages
    }
  }
}
"""

GET_COMPANY = """
query get_company($company_id: ID!) {
    company(id: $company_id) {
      id
      label
      customFeatures
    }
}
"""

GET_COMPANIES = """
query Companies {
  companies (
    limit: 50, 
    order: label,
    orderType: ASC
  )  {
    collection {
      id
      label
      customFeatures
    }
  }
}
"""

GET_ISSUES_FINGERPRINT = """
query GetIssuesFingerprint(
    $company_id: ID!,
    $page: Int,
    $per_page: Int,
    $asset_id: [ID!],
    $statuses: [IssueStatusLabel!]
    $failure_types: [Issue!]
) {
    issues(
        companyId: $company_id,
        pagination: {
            page: $page,
            perPage: $per_page
        },
        filters: {
            assetIds: $asset_id,
            statuses: $statuses,
            failureTypes: $failure_types
        }
    ) {
        collection {
            id
            type
            ... on FindingInterface {
                originalIssueIdFromTool
                scanSource
            }
            status
        }
        metadata {
            totalCount
            totalPages
        }
    }
}
"""

GET_DEPLOYS_BY_ASSET = """
query GetDeploysByAsset(
  $asset_id: ID!
) {
  deploysByAsset(
    assetId: $asset_id
  ) {
    collection {
      currentCommit
      previousCommit
    }
  }
}
"""