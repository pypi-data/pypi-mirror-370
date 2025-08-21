import requests

from convisoappsec.common.graphql.error_handlers import GraphQlErrorHandler, RequestErrorHandler
from convisoappsec.version import __version__


class GraphQLClient:
    DEFAULT_HEADERS = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        "User-Agent": "AST:{version}".format(version=__version__),
    }

    def __init__(self, url, headers={}):
        self.url = url
        self.__session = requests.Session()
        self.__session.headers.update(
            **self.DEFAULT_HEADERS,
            **headers
        )

    def execute(self, query, variables={}):
        try:
            payload = self._build_graphql_payload(query, variables)

            response = self.__session.post(
                url=self.url,
                json=payload,
            )

            response.raise_for_status()

        except Exception as e:
            handler = RequestErrorHandler(e)
            handler.handle_request_error()

        json_response = response.json()
        graphql_handler = GraphQlErrorHandler(json_response)
        graphql_handler.raise_on_graphql_error()
        graphql_handler.raise_on_graphql_body_error()

        return json_response['data']

    @staticmethod
    def _build_graphql_payload(query, variables):
        data = {
            'query': query,
            'variables': variables
        }

        return data
