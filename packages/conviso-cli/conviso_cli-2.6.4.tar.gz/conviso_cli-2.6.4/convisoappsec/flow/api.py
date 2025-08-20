import copy
import json
from contextlib import suppress
from os import SEEK_SET
from urllib.parse import urljoin

import jsonschema
import requests

PRODUCTION_API_URL = "https://api.convisoappsec.com"
STAGING_API_URL = "https://staging.convisoappsec.com"
DEVELOPMENT_API_URL = "http://localhost:3000"
DEFAULT_API_URL = PRODUCTION_API_URL


class RequestsSession(requests.Session):

    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.base_url, url)

        return super().request(
            method, url, *args, **kwargs
        )


class FlowAPIException(Exception):
    pass


class FlowAPIAccessDeniedException(FlowAPIException):
    pass


class DeployNotFoundException(FlowAPIException):
    pass


class DockerRegistry(object):
    SAST_ENDPOINT = '/auth/public_auth'

    def __init__(self, client):
        self.client = client

    def get_sast_token(self):
        session = self.client.requests_session
        response = session.get(self.SAST_ENDPOINT)
        response.raise_for_status()
        return response.text


class RESTClient(object):

    def __init__(
        self,
        url=STAGING_API_URL,
        key=None,
        insecure=False,
        user_agent=None,
        ci_provider_name=None
    ):
        self.url = url
        self.insecure = insecure
        self.key = key
        self.user_agent = user_agent
        self.ci_provider_name = ci_provider_name

    @property
    def requests_session(self):
        session = RequestsSession(self.url)
        session.verify = not self.insecure

        session.headers.update({
            'x-api-key': self.key,
            'x-flowcli-ci-provider-name': self.ci_provider_name
        })

        if self.user_agent:
            user_agent_header = {}
            name = self.user_agent.get('name')
            version = self.user_agent.get('version')

            if name and version:
                user_agent_header_fmt = "{name}/{version}"
                user_agent_header_content = user_agent_header_fmt.format(
                    name=name,
                    version=version,
                )

                user_agent_header = {
                    'User-Agent': user_agent_header_content
                }

            session.headers.update(user_agent_header)

        return session


    @property
    def docker_registry(self):
        return DockerRegistry(self)
