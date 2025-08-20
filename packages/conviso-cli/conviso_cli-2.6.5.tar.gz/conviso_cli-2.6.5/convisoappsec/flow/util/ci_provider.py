from enum import Enum
from functools import reduce


class CIProvider(Enum):
    AWS_CODEBUILD = {
        '_env_vars': [
            'CODEBUILD_BUILD_ARN',
            'CODEBUILD_BUILD_ID',
            'CODEBUILD_BUILD_NUMBER'
        ]
    }
    AZURE_PIPELINES = {
        '_env_vars': [
            'SYSTEM_JOBDISPLAYNAME',
            'SYSTEM_JOBID',
            'SYSTEM_TEAMPROJECT'
        ]
    }
    BITBUCKET = {
        '_env_vars': [
            'BITBUCKET_PROJECT_KEY',
            'BITBUCKET_PROJECT_UUID',
            'BITBUCKET_PIPELINE_UUID'
        ]
    }
    CIRCLECI = {
        '_env_vars': [
            'CIRCLECI',
            'CIRCLE_JOB',
            'CIRCLE_USERNAME'
        ]
    }
    CODEFRESH = {
        '_env_vars': [
            'CF_REPO_NAME',
            'CF_REVISION',
            'CF_BRANCH'
        ]
    }
    GITLAB = {
        '_env_vars': [
            'GITLAB_CI',
            'CI_PROJECT_ID',
            'CI_SERVER_NAME'
        ]
    }
    GITHUB = {
        '_env_vars': [
            'GITHUB_REPOSITORY',
            'GITHUB_REF',
            'GITHUB_JOB'
        ]
    }
    JENKINS = {
        '_env_vars': [
            'BUILD_NUMBER',
            'BUILD_TAG',
            'JOB_NAME'
        ]
    }
    OTHER = {
        '_env_vars': []
    }


    @classmethod
    def names(cls):
        return [provider.name for provider in cls]


    def env_vars_exists(self, env):
        provider_vars = self.__provider_vars

        if not provider_vars:
            return False

        compute_found_env_vars = ComputeFoundEnvVars(env)

        found_vars = reduce(compute_found_env_vars, provider_vars, 0)
        vars_length = len(provider_vars)

        return found_vars == vars_length


    @property
    def __provider_vars(self):
        return self.value['_env_vars']


class ComputeFoundEnvVars:
    def __init__(self, environment):
        self.__environment = environment

    def __call__(self, found_vars, env_var_name):
        if self.__environment.get(env_var_name):
            return found_vars + 1
        else:
            0