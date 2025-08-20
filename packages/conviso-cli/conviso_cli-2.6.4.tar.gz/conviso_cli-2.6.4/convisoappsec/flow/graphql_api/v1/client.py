from convisoappsec.common.graphql.low_client import GraphQLClient
from convisoappsec.flow.graphql_api.v1.resources_api import AssetsAPI, CompaniesApi, IssuesApi, DeploysApi, \
    SbomApi, LogAstError, ContainerApi, ControlSyncStatus


class ConvisoGraphQLClient():
    DEFAULT_AUTHORIZATION_HEADER_NAME = 'x-api-key'

    def __init__(self, api_url, api_key):
        headers = {
            self.DEFAULT_AUTHORIZATION_HEADER_NAME: api_key
        }

        self.__low_client = GraphQLClient(api_url, headers)

    @property
    def assets(self):
        return AssetsAPI(self.__low_client)

    @property
    def companies(self):
        return CompaniesApi(self.__low_client)

    @property
    def issues(self):
        return IssuesApi(self.__low_client)

    @property
    def deploys(self):
        return DeploysApi(self.__low_client)

    @property
    def sbom(self):
        return SbomApi(self.__low_client)

    @property
    def container(self):
        return ContainerApi(self.__low_client)

    @property
    def ast_errors(self):
        return LogAstError(self.__low_client)

    @property
    def control_sync_status(self):
        return ControlSyncStatus(self.__low_client)
