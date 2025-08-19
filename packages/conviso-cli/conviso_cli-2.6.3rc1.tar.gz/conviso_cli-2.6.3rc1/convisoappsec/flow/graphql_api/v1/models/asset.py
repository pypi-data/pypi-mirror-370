class AssetInput:
    def __init__(self, company_id, name, scan_type=None, repo_url=None):
        self.name = name
        self.company_id = company_id
        self.scan_type = scan_type
        self.repo_url = repo_url

    def to_graphql_dict(self):
        return {
            "companyId": self.company_id,
            "name": self.name,
            "scanType": self.scan_type,
            "repoUrl": self.repo_url
        }
