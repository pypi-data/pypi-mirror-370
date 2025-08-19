import logging

logging.basicConfig(
    filename='output.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(levelname)s:  %(filename)s:  %(threadName)s:  %(name)s:  %(message)s'
)

LOGGER = logging.getLogger(__name__)


def log_and_notify_ast_event(flow_context, company_id, asset_id, ast_log):
    """
    Logs an AST (Application Security Test) event for a specific company and asset,
    and sends notifications.

    This method performs the following actions:
    1. Sends the provided AST log to a monitoring platform like Datadog for logging and tracking.
    2. Sends a Slack notification with relevant details about the AST event.

    Args:
        flow_context: The context of the AST execution.
        company_id (int): The ID of the company for which the AST event is being logged.
        asset_id (int): The ID of the asset associated with the AST event.
        ast_log (string): A string with the log details of the AST event.
    """
    conviso_api = flow_context.create_conviso_graphql_client()
    conviso_api.ast_errors.send_ast_error(company_id = company_id, asset_id = asset_id, log = ast_log)
