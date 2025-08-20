import jmespath
from convisoappsec.flow.graphql_api.beta.models.issues.iac import CreateIacFindingInput
from convisoappsec.flow.graphql_api.beta.models.issues.sast import CreateSastFindingInput
from convisoappsec.flow.graphql_api.beta.models.issues.sca import CreateScaFindingInput
from convisoappsec.flow.graphql_api.beta.models.issues.container import CreateOrUpdateContainerFindingInput
from convisoappsec.flow.graphql_api.beta.schemas import mutations
from convisoappsec.flow.graphql_api.v1.schemas import resolvers


class IssuesAPI(object):
    """ To operations on Issues's (aka, findings and vulnerabilities)) in Conviso Platform. """

    def __init__(self, conviso_graphql_client):
        self.__conviso_graphql_client = conviso_graphql_client

    def create_sast(self, sast_issue_model: CreateSastFindingInput):
        graphql_variables = {
            "input": sast_issue_model.to_graphql_dict()
        }

        graphql_body_response = self.__conviso_graphql_client.execute(
            mutations.CREATE_SAST_FINDING_INPUT,
            graphql_variables
        )

        expected_path = 'createSastFinding.issue'

        issue = jmespath.search(
            expected_path,
            graphql_body_response,
        )

        return issue

    def create_sca(self, sca_issue_model: CreateScaFindingInput):
        graphql_variables = {
            "input": sca_issue_model.to_graphql_dict()
        }

        graphql_body_response = self.__conviso_graphql_client.execute(
            mutations.CREATE_SCA_FINDING_INPUT,
            graphql_variables
        )

        expected_path = 'createScaFinding.issue'

        issue = jmespath.search(
            expected_path,
            graphql_body_response,
        )

        return issue

    def create_iac(self, issue_model: CreateIacFindingInput):
        graphql_variables = {
            "input": issue_model.to_graphql_dict()
        }

        graphql_body_response = self.__conviso_graphql_client.execute(
            mutations.CREATE_SAST_FINDING_INPUT,
            graphql_variables
        )

        expected_path = 'createSastFinding.issue'

        issue = jmespath.search(
            expected_path,
            graphql_body_response,
        )

        return issue

    def create_container(self, container_issue_model: CreateOrUpdateContainerFindingInput):
        graphql_variables = {
            "input": container_issue_model.to_graphql_dict()
        }

        graphql_body_response = self.__conviso_graphql_client.execute(
            mutations.CREATE_CONTAINER_FINDING_INPUT,
            graphql_variables
        )

        expected_path = 'createOrUpdateContainerFinding.issue'

        issue = jmespath.search(
            expected_path,
            graphql_body_response,
        )

        return issue

    def auto_close_vulnerabilities(self, company_id, asset_id, statuses, page=1, vulnerability_type=None):
        """ entry point for auto closing vulnerabilities on conviso platform """
        if vulnerability_type is None:
            vulnerability_type = ['SAST_FINDING', 'SCA_FINDING']

        graphql_variables = {
            'company_id': company_id,
            'asset_id': asset_id,
            'page': page,
            'per_page': 100,
            'statuses': statuses,
            'failure_types': vulnerability_type
        }

        graphql_body_response = self.__conviso_graphql_client.execute(
            resolvers.GET_ISSUES_FINGERPRINT,
            graphql_variables
        )

        expected_path = 'issues'

        issues = jmespath.search(
            expected_path,
            graphql_body_response
        )

        return issues

    def update_issue_status(self, issue_id, status, reason):
        """ Update issue status on conviso platform """

        graphql_variables = {
            'issueId': issue_id,
            'status': status,
            'reason': reason
        }

        graphql_body_response = self.__conviso_graphql_client.execute(
            mutations.UPDATE_ISSUE_STATUS,
            graphql_variables
        )

        expected_path = 'changeIssueStatus.issue'

        issue = jmespath.search(
            expected_path,
            graphql_body_response,
        )

        return issue
