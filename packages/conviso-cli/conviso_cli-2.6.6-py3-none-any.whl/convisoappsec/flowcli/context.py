import click

from convisoappsec.common import safe_join_url
from convisoappsec.flow import api
from convisoappsec.flow.graphql_api.beta.client import ConvisoGraphQLClientBeta
from convisoappsec.flow.graphql_api.v1.client import ConvisoGraphQLClient
from convisoappsec.version import __version__


class FlowContext(object):
    def __init__(self):
        self.key = None
        self.url = None
        self.insecure = None
        self.ci_provider = None
        self.logger = None

    def create_conviso_rest_api_client(self):
        return api.RESTClient(
            key=self.key,
            url=self.url,
            insecure=self.insecure,
            user_agent={
                'name': 'flowcli',
                'version': __version__,
            },
            ci_provider_name=self.ci_provider.name
        )

    def create_conviso_graphql_client(self):
        url = safe_join_url(self.url, "/graphql")

        return ConvisoGraphQLClient(
            api_url=url,
            api_key=self.key
        )

    def create_conviso_api_client_beta(self):
        url = safe_join_url(self.url, "/graphql")

        return ConvisoGraphQLClientBeta(
            api_url=url,
            api_key=self.key,
        )


pass_flow_context = click.make_pass_decorator(
    FlowContext, ensure=True
)
