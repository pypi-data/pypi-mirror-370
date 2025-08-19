import io
import sys
from shlex import quote

import click
import requests

from convisoappsec.flow.util.ci_provider import CIProvider

class CreateDeployException(Exception):
    pass

class PerformDeployException(Exception):
    pass

class DeployFormatter(object):
    DEFAULT = 'default'
    ENV_VARS = 'env_vars'

    def __init__(self, format):
        self.stategy = self._select_strategy(format)

    def format(self, deploy):
        return self.stategy(deploy)

    def _select_strategy(self, format):
        format_strategies = {
            self.DEFAULT: self.default_format,
            self. ENV_VARS: self.env_vars_format,
        }

        strategy = format_strategies.get(format)

        if not strategy:
            msg_fmt = "Allowed deploy formats[{0}]. Given {1}"
            msg = msg_fmt.format(
                "|".join(self.FORMATS()),
                format,
            )

            raise ValueError(msg)

        return strategy

    @classmethod
    def FORMATS(cls):
        return [
            cls.DEFAULT,
            cls.ENV_VARS,
        ]

    def env_vars_format(self, deploy):
        to_env_vars_translation_args = [
            # (env_var_name, attrib_name, attrib_default_val)
            ('FLOW_DEPLOY_ID', 'id', 0),
            ('FLOW_DEPLOY_CREATED_AT', 'created_at', ''),
            ('FLOW_DEPLOY_CURRENT_VERSION_TAG', 'current_tag', ''),
            ('FLOW_DEPLOY_PREVIOUS_VERSION_TAG', 'previous_tag', ''),
            ('FLOW_DEPLOY_CURRENT_VERSION_COMMIT', 'current_commit', ''),
            ('FLOW_DEPLOY_PREVIOUS_VERSION_COMMIT', 'previous_commit', ''),
            ('CONVISO_DEPLOY_ID', 'id', 0),
            ('CONVISO_DEPLOY_CREATED_AT', 'created_at', ''),
            ('CONVISO_DEPLOY_CURRENT_VERSION_TAG', 'current_tag', ''),
            ('CONVISO_DEPLOY_PREVIOUS_VERSION_TAG', 'previous_tag', ''),
            ('CONVISO_DEPLOY_CURRENT_VERSION_COMMIT', 'current_commit', ''),
            ('CONVISO_DEPLOY_PREVIOUS_VERSION_COMMIT', 'previous_commit', ''),
        ]

        env_vars = {}

        for arg in to_env_vars_translation_args:
            env_var_name, attrib_name, attrib_default_val = arg

            env_var_val = env_vars[env_var_name] = deploy.get(
                attrib_name, attrib_default_val
            )

            env_vars[env_var_name] = str(env_var_val)

        buffer = io.StringIO()

        for var_name, var_val in env_vars.items():
            line_fmt = "export {name}={value}"
            line = line_fmt.format(
                name=quote(var_name),
                value=quote(var_val),
            )

            print(line, file=buffer)

        buffer.seek(0)
        return buffer.read()

    def default_format(self, src_deploy):
        deploy = {
            'id': 0,
            'current_tag': '',
            'previous_tag': '',
            'current_commit': '',
            'previous_commit': '',
            'created_at': '',
        }

        deploy.update(src_deploy)

        default_fmt = '''
Deploy stats:
  current_version.commit={current_commit}
  current_version.tag={current_tag}
  previous_version.commit={previous_commit}
  previous_version.tag={previous_tag}
        '''

        return default_fmt.format(
            **deploy
        )


def notify_created_deploy(deploy):
    formatter = DeployFormatter(DeployFormatter.DEFAULT)
    click.echo(formatter.format(deploy))


def asset_id_option(*args, **kwargs):
    kwargs["envvar"] = kwargs.get("envvar", ("CONVISO_ASSET_ID", "FLOW_ASSET_ID"))
    kwargs["show_envvar"] = kwargs.get("show_envvar", True)
    kwargs["required"] = kwargs.get("required", False)
    kwargs["hidden"] = kwargs.get("hidden", False)
    asset_id_param = "--asset-id"
    paramsdecl = args

    if asset_id_param not in args:
        paramsdecl = args + (asset_id_param, )

    return click.option(
        *paramsdecl,
        type=int,
        **kwargs
    )

def on_http_error(error):
    try:
        raise error
    except requests.exceptions.HTTPError as e:
        message = error.response.text

        if not message:
            return

        click.echo(
            "HttpErrorResponse: {0}".format(message),
            file=sys.stderr
        )


def __try_retrieve_ci_provider(provider_name):
    try:
        return CIProvider[provider_name]
    except KeyError as e:
        error_msg_fmt = 'Received for parameter provider_name[{}]. Expected values are: [{}]'
        expected_values = '|'.join(CIProvider.names())
        error_msg = error_msg_fmt.format(provider_name, expected_values)

        raise ValueError(error_msg) from e


def process_ci_provider_option(provider_name, env={}):
    if provider_name is not None:
        return __try_retrieve_ci_provider(provider_name)

    for provider in CIProvider:
        if provider.env_vars_exists(env):
            return provider

    return CIProvider.OTHER
