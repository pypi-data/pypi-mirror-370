CREATE_ASSET = """ 
mutation (
  $companyId: Int!,
  $name: String!,
  $scanType: AssetScan!
) {
  createAsset(
    input: {
      companyId: $companyId,
      name: $name,
      scanType: $scanType
    }
  ) {
    asset {
      id
      name
      createdAt
    }
    errors
  }
}
"""

UPDATE_ASSET = """
mutation (
  $id: ID!,
  $companyId: Int!,
  $name: String!,
  $tecnologyList: [String!],
  $repoUrl: String
) {
  updateAsset(
    input: {
      id: $id,
      companyId: $companyId,
      name: $name,
      tecnologyList: $tecnologyList,
      repoUrl: $repoUrl
    }
  ) {
    asset {
      id
    }
  }
}
"""

IMPORT_SBOM = """
mutation (
  $file: Upload!,
  $assetId: ID!,
  $companyId: ID!
) {
  importSbom(
    input: {
      file: $file,
      assetId: $assetId,
      companyId: $companyId
    }
  ) {
    success
  }
}
"""

IMPORT_CONTAINER = """
mutation (
  $file: Upload!,
  $assetId: ID!,
  $companyId: ID!
) {
  importContainerFindingsFile(
    input: {
      file: $file,
      assetId: $assetId,
      companyId: $companyId
    }
  ) {
    success
  }
}
"""

LOG_AST_ERROR = """
mutation (
  $companyId: ID!,
  $assetId: ID!,
  $log: String!
) {
  logAstError(
    input: {
      companyId: $companyId,
      assetId: $assetId,
      log: $log
    }
  ) {
    success
  }
}
"""

CREATE_DEPLOY = """
mutation (
  $assetId: ID!,
  $previousCommit: String!,
  $currentCommit: String!,
  $branchName: String,
  $diffContent: Upload!,
  $commitHistory: Upload!
) {
  createDeploy(
    input: {
      assetId: $assetId,
      previousCommit: $previousCommit,
      currentCommit: $currentCommit,
      branchName: $branchName,
      diffContent: $diffContent,
      commitHistory: $commitHistory
    }
  ) {
    deploy {
      id
    }
  }
}
"""

IMPORT_FINDINGS = """
mutation (
  $file: Upload!,
  $assetId: ID!,
  $companyId: ID!
  $vulnerabilityTypes: [Issue!]!
  $deployId: ID
  $commitRef: String
  $controlSyncStatusId: ID
) {
  importAstFindingsFile(
    input: {
      file: $file,
      assetId: $assetId,
      companyId: $companyId,
      vulnerabilityTypes: $vulnerabilityTypes,
      deployId: $deployId,
      commitRef: $commitRef
      controlSyncStatusId: $controlSyncStatusId
    }
  ) {
    success
  }
}
"""

CREATE_CONTROL_SYNC_STATUS = """
mutation ($assetId: ID!) {
  createControlSyncStatus(
    input: {
      assetId: $assetId,
      integration: CONVISO_AST,
      externalVulnerabilityCount: 0
    }
  ) {
    controlSyncStatus {
      id
    }
    success
  }
}
"""

UPDATE_CONTROL_SYNC_STATUS = """
mutation ($id: ID!) {
  updateControlSyncStatus(
    input: {
      id: $id
      externalVulnerabilityCount: 1
    }
  ) {
    controlSyncStatus {
      id
    }
  }
}
"""

INCREASE_ISSUE_SCAN_COUNT = """
mutation (
  $controlSyncStatusId: ID!
  $assetId: ID!
  $successCount: Int
  $failureCount: Int
  $failureReason: String
) {
  increaseIssueScanCount(
    input: {
      controlSyncStatusId: $controlSyncStatusId
      assetId: $assetId
      successCount: $successCount
      failureCount: $failureCount
      failureReason: $failureReason
      integration: CONVISO_AST
    }
  ) {
    controlSyncStatus {
	  id
	}
  }
}
"""
