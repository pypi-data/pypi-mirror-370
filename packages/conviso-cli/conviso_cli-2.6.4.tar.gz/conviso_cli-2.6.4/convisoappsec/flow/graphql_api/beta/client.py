
from convisoappsec.common.graphql.low_client import GraphQLClient
from convisoappsec.flow.graphql_api.beta.resources_api import IssuesAPI


class ConvisoGraphQLClientBeta():
    DEFAULT_AUTHORIZATION_HEADER_NAME = 'x-api-key'

    def __init__(self, api_url, api_key):
        headers = {
            self.DEFAULT_AUTHORIZATION_HEADER_NAME: api_key
        }

        self.__low_client = GraphQLClient(api_url, headers)

    @property
    def issues(self):
        return IssuesAPI(self.__low_client)
