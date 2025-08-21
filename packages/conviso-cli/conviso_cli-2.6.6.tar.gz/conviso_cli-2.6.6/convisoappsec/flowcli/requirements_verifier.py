import re
from convisoappsec.flowcli.common import CreateDeployException
from convisoappsec.logger import LOGGER
from convisoappsec.flowcli.companies.ls import Companies
from convisoappsec.flow.graphql_api.v1.models.asset import AssetInput
from convisoappsec.common.git_data_parser import GitDataParser
from .context import pass_flow_context


class RequirementsVerifier:

    @staticmethod
    @pass_flow_context
    def list_assets(flow_context, company_id, asset_name, scan_type):
        conviso_api = flow_context.create_conviso_graphql_client()

        asset_model = AssetInput(
            int(company_id),
            asset_name,
            scan_type
        )

        return conviso_api.assets.list_assets(asset_model)

    @staticmethod
    @pass_flow_context
    def create_asset(flow_context, company_id, asset_name, scan_type):
        conviso_api = flow_context.create_conviso_graphql_client()

        asset_model = AssetInput(
            int(company_id),
            asset_name,
            scan_type
        )

        return conviso_api.assets.create_asset(asset_model)

    @staticmethod
    def sarif_asset_assignment(context, asset):
        """ assignment asset when is a sarif import """
        context.params['asset_id'] = asset['id']
        context.params['experimental'] = True

        return context

    @staticmethod
    def find_or_create_asset(context, company_id, old_name, new_name):
        """ Method to find or create asset on conviso platform """
        try:
            existing_assets = RequirementsVerifier.list_assets(company_id, new_name, 'SAST')
            if not existing_assets:
                existing_assets = RequirementsVerifier.list_assets(company_id, old_name, 'SAST')
            for asset in existing_assets:
                if asset['name'] == old_name or asset['name'] == new_name:
                    LOGGER.info('✅ Asset found...')
                    context.params['asset_name'] = asset['name']
                    return [asset]
            LOGGER.info('💬 Asset not found; creating...')
            new_asset = RequirementsVerifier.create_asset(company_id, new_name, 'SAST')
            context.params['asset_name'] = new_name
            return [new_asset]
        except Exception as e:
            raise Exception("Error: {}".format(e))

    @staticmethod
    def create_asset_with_custom_name(context, company_id, asset_name):
        """ Create an asset with custom name pass with a custom name """
        if not asset_name or not asset_name.strip():  # Check for None or blank string
            raise ValueError("Asset name cannot be None or blank.")

        # we need to verify if already has an asset with the name provided.
        # because graphql will return an error if already has.
        existing_asset = RequirementsVerifier.list_assets(company_id, asset_name, 'SAST')

        if not existing_asset:
            LOGGER.info("💬 Asset not found; creating with name {}...".format(asset_name))
            asset = RequirementsVerifier.create_asset(company_id, asset_name, 'SAST')
        else:
            LOGGER.info('✅ Asset found...')
            asset = existing_asset[0]

        context.params['asset_name'] = asset_name

        return asset

    @staticmethod
    @pass_flow_context
    def prepare_context(flow_context, context, from_ast=False):
        """ Due to the new vulnerability management we need to do some checks before continuing the flow """

        if from_ast is True:
            context.params['from_ast'] = True

        companies = Companies()
        company_id = context.params['company_id']

        if company_id is not None:
            companies_filtered = [companies.ls(flow_context, company_id=company_id)]
        else:
            companies_filtered = companies.ls(flow_context)

        if len(companies_filtered) > 1:
            raise CreateDeployException(
                "❌ Deploy not created. You have access to multiple companies; please specify one using CONVISO_COMPANY_ID."
            )

        company = companies_filtered[0]
        company_id = company['id']

        if context.params['asset_name'] is not None:
            # if user use --asset-name param or envvar CONVISO_ASSET_NAME, FLOW_ASSET_NAME
            asset_name = context.params['asset_name']
            asset = RequirementsVerifier.create_asset_with_custom_name(context, company_id, asset_name)
        else:
            pattern = r"\([^)]*\)"  # eliminating what is in parentheses
            old_asset_name = GitDataParser(context.params['repository_dir']).parse_name()
            new_asset_name = re.sub(pattern, '', old_asset_name).strip()

            assets = RequirementsVerifier.find_or_create_asset(context, company_id, old_asset_name, new_asset_name)
            asset = assets[0]

        if 'input_file' in context.params:
            # sarif only uses assets, not requiring the creation of a project.
            RequirementsVerifier.sarif_asset_assignment(context, asset)

            return context

        context.params['asset_id'] = asset['id']
        context.params['experimental'] = True
        context.params['company_id'] = company_id

        return context
