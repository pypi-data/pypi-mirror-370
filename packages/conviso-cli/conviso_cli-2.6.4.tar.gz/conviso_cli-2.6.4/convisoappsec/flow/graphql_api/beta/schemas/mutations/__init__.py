CREATE_SAST_FINDING_INPUT = """
mutation createSastFinding($input: CreateSastFindingInput!) {
  createSastFinding(input: $input) {
    issue {
      id
    }
  }
}
"""

CREATE_SCA_FINDING_INPUT = """
mutation createScaFinding($input: CreateScaFindingInput!) {
    createScaFinding(input: $input) {
        issue {
            id
        }
    }
}
"""

CREATE_IAC_FINDING_INPUT = """
mutation createOrUpdateIacFinding($input: CreateOrUpdateSastFindingInput!) {
    createOrUpdateIacFinding(input: $input) {
        issue {
            id
        }
    }
}
"""

CREATE_CONTAINER_FINDING_INPUT = """
mutation createOrUpdateContainerFinding($input: CreateOrUpdateContainerFindingInput!) {
    createOrUpdateContainerFinding(input: $input) {
        issue {
            id
        }
    }
}
"""

UPDATE_ISSUE_STATUS = """
mutation (
  $issueId: ID!,
  $status: IssueStatusLabel!,
  $reason: String
) {
  changeIssueStatus (
    input: {
      id: $issueId
      status: $status
      reason: $reason
    }
  ) {
    issue {
      id
    }
  }
}
"""
