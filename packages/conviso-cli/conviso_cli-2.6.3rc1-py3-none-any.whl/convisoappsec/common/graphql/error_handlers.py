import requests
import jmespath

from convisoappsec.common.graphql.errors import AuthenticationError, Error, ResponseError, ServerError


class RequestErrorHandler:
    def __init__(self, error):
        self.error = error

    def handle_request_error(self):
        try:
            raise self.error
        except requests.exceptions.HTTPError as e:
            self._handle_http_error(e)
        except Exception as e:
            self._handle_unexpected_error(e)

    @staticmethod
    def _handle_unexpected_error(error):
        raise Error(str(error)) from error

    @staticmethod
    def _handle_http_error(error):
        if error.response.status_code == 401:
            error_msg_fmt = 'Unauthorized access, check your credentials. {}'
            response = error.response.json()
            error_messages = response.get('errors', [])
            error_msg = error_msg_fmt.format(error_messages)

            raise AuthenticationError(error_msg) from error

        if error.response.status_code == 500:
            error_msg_fmt = 'Internal Server Error. {}'
            error_msg = error_msg_fmt.format(error.response.text)

            raise ServerError(error_msg) from error

        raise Error(error.response.text) from error


class GraphQlErrorHandler:
    def __init__(self, response):
        self.response = response

    def raise_on_graphql_body_error(self):
        data = self.response.get('data', [])

        for key in data:
            if data[key] is None:
                continue

            errors = data[key].get('errors', [])
            has_errors = len(errors) > 0
            if has_errors:
                raise ResponseError(errors)

    def raise_on_graphql_error(self):
        errors = self.response.get('errors', [])

        if not errors:
            return

        error = errors[0]

        error_path = 'extensions.code'
        
        code = jmespath.search(
            error_path,
            error
        )

        message = error.get('message', '')

        raise ResponseError(message, code)
