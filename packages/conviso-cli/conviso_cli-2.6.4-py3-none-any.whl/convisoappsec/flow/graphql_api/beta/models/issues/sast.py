from convisoappsec.flow.graphql_api.beta.models.issues.normalize import Normalize

class CreateSastFindingInput:
    def __init__(
        self,
        asset_id,
        code_snippet,
        file_name,
        vulnerable_line,
        first_line,
        title,
        description,
        severity,
        reference,
        category,
        original_issue_id_from_tool,
        solution,
        control_sync_status_id
    ):
        self.asset_id = asset_id
        self.severity = Normalize.normalize_severity(severity)
        self.title = title
        self.description = description
        self.code_snippet = code_snippet
        self.file_name = file_name
        self.vulnerable_line = int(vulnerable_line)
        self.first_line = int(first_line)
        self.reference = reference
        self.category = category
        self.original_issue_id_from_tool = original_issue_id_from_tool
        self.solution = solution
        self.control_sync_status_id = control_sync_status_id

    def to_graphql_dict(self):
        """
        This function returns a dictionary containing various attributes of an
        asset in a GraphQL format.
        """
        return {
            "assetId": int(self.asset_id),
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "codeSnippet": self.code_snippet,
            "fileName": self.file_name,
            "vulnerableLine": int(self.vulnerable_line),
            "firstLine": int(self.first_line),
            "reference": self.reference,
            "category": str(self.category),
            "originalIssueIdFromTool": str(self.original_issue_id_from_tool),
            "solution": str(self.solution),
            "controlSyncStatusId": str(self.control_sync_status_id)
        }
