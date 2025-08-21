import time
import traceback
from convisoappsec.logger import LOGGER, log_and_notify_ast_event


class RetryHandler:
    def __init__(self, flow_context=None, company_id=None, asset_id=None):
        self.max_retries = 5
        self.initial_delay = 1
        self.backoff_factor = 2
        self.flow_context = flow_context
        self.company_id = company_id
        self.asset_id = asset_id

    def execute_with_retry(self, func, *args, **kwargs):
        """Execute a function with retry logic and exponential backoff."""
        retries = 0
        delay = self.initial_delay

        while retries < self.max_retries:
            try:
                return func(*args, **kwargs)
            except Exception:
                retries += 1
                time.sleep(delay)
                delay *= self.backoff_factor

                if retries == self.max_retries:
                    full_trace = traceback.format_exc()
                    LOGGER.warning(
                        "⚠️ Maximum retries reached. Our technical team has been notified."
                    )

                    try:
                        log_and_notify_ast_event(
                            flow_context=self.flow_context, company_id=self.company_id, asset_id=self.asset_id,
                            ast_log=full_trace
                        )
                    except Exception as log_error:
                        LOGGER.warning(f"⚠️ Failed to log and notify AST event: {log_error}")
