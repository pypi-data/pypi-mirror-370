from datetime import datetime, timezone


class CreateProjectInput:
    def __init__(self, company_id, asset_id, label):
        self.company_id = company_id
        self.asset_id = asset_id
        self.label = label

    def to_graphql_dict(self):
        current_datetime = datetime.now(timezone.utc)
        formatted_date = current_datetime.isoformat()

        return {
            "companyId": int(self.company_id),
            "assetsIds": int(self.asset_id),
            "label": self.label,
            "startDate": str(formatted_date),
            "typeId": 33,
            "playbooksIds": 1,
            "goal": '',
            "scope": self.company_id
        }


class UpdateProjectInput:
    def __init__(self, project_id, asset_id):
        self.project_id = project_id
        self.asset_id = asset_id

    def to_graphql_dict(self):
        return {
            "projectId": int(self.project_id),
            "assetsIds": [int(self.asset_id)],
        }
