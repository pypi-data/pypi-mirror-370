import click
from convisoappsec.flowcli.common import on_http_error
from convisoappsec.common import safe_join_url
from convisoappsec.flow.graphql_api.v1.client import ConvisoGraphQLClient

class Companies():
    def ls(self, flow_context, company_id=None):
        api_key = flow_context.key

        try:
            url = safe_join_url(flow_context.url, "/graphql")
            conviso_api = ConvisoGraphQLClient(api_url=url,api_key=api_key)

            return perform_command(conviso_api, company_id)
        except Exception as exception:
            on_http_error(exception)
            raise click.ClickException(str(exception)) from exception

def perform_command(conviso_api, company_id):
    if company_id is not None:
        companies = conviso_api.companies.get_company_by_id(company_id)
    else:
        companies = conviso_api.companies.get_companies()

    return companies
