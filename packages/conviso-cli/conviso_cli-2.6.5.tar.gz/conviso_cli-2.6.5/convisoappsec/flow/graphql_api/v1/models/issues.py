class IssuesInput:
    def __init__(self, company_id, asset_id, page=1, per_page=50):
        self.company_id = company_id
        self.asset_id = asset_id
        self.page = page
        self.per_page = per_page
        self.statuses = ['CREATED', 'IDENTIFIED']

    def to_graphql_dict(self):
        return {
            "companyId": self.company_id,
            "page": self.page,
            "perPage": self.per_page,
            "assetIds": self.asset_id,
            "statuses": self.statuses
        }
