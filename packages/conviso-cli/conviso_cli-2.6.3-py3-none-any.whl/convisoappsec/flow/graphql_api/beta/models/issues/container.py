from convisoappsec.flow.graphql_api.beta.models.issues.normalize import Normalize


class CreateOrUpdateContainerFindingInput:
    def __init__(
            self,
            asset_id,
            title,
            description,
            severity,
            solution,
            reference,
            affected_version,
            package,
            cve,
            patched_version,
            category,
            original_issue_id_from_tool
    ):
        self.asset_id = asset_id
        self.title = title
        self.description = description
        self.severity = Normalize.normalize_severity(severity)
        self.solution = solution
        self.reference = reference
        self.affected_version = affected_version
        self.package = package
        self.patched_version = patched_version
        self.original_issue_id_from_tool = original_issue_id_from_tool
        self.category = self.process_field(category)
        self.cve = self.process_field(cve)

    def to_graphql_dict(self):
        """
        This function returns a dictionary containing various attributes of an
        asset in a GraphQL format.
        """
        return {
            "assetId": int(self.asset_id),
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "solution": self.solution,
            "reference": self.reference,
            "affectedVersion": self.affected_version,
            "package": self.package,
            "cve": self.cve,
            "patchedVersion": self.patched_version,
            "category": self.category,
            "originalIssueIdFromTool": self.original_issue_id_from_tool
        }

    @staticmethod
    def process_field(value):
        """
        Processes a field to ensure it is converted into a string.

        - If the value is a list, it joins the items into a comma-separated string.
        - If the value is a string, it returns the string as is.
        - If the value is neither a list nor a string, it returns an empty string.

        Args:
            value (list | str | Any): The value to process.

        Returns:
            str: The processed string representation of the value.
        """
        if isinstance(value, list):
            return ' , '.join(value)
        elif isinstance(value, str):
            return value
        return ''
