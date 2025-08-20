import click
import click_log
import json
from base64 import b64decode
from re import search as regex_search
from copy import deepcopy as clone
from convisoappsec.flowcli import help_option
from convisoappsec.flowcli.context import pass_flow_context
from convisoappsec.logger import LOGGER
from convisoappsec.flowcli.requirements_verifier import RequirementsVerifier
from convisoappsec.flow.graphql_api.beta.models.issues.sast import (CreateSastFindingInput)
from convisoappsec.flow.graphql_api.beta.models.issues.sca import CreateScaFindingInput
from convisoappsec.common.graphql.errors import ResponseError

click_log.basic_config(LOGGER)


@click.command()
@click.option(
    "-i",
    "--input-file",
    required=True,
    type=click.Path(exists=True),
    help='The path to SARIF file.',
)
@click.option(
    "--company-id",
    required=False,
    envvar=("CONVISO_COMPANY_ID", "FLOW_COMPANY_ID"),
    help="Company ID on Conviso Platform",
)
@click.option(
    "-r",
    "--repository-dir",
    default=".",
    show_default=True,
    type=click.Path(
        exists=True,
        resolve_path=True,
    ),
    required=False,
    help="The source code repository directory.",
)
@click.option(
    '--asset-name',
    required=False,
    envvar=("CONVISO_ASSET_NAME", "FLOW_ASSET_NAME"),
    help="Provides a asset name.",
)
@help_option
@pass_flow_context
@click.pass_context
def import_sarif(context, flow_context, input_file, company_id, repository_dir, asset_name):
    context.params['company_id'] = company_id if company_id is not None else None
    context.params['repository_dir'] = repository_dir

    prepared_context = RequirementsVerifier.prepare_context(clone(context))
    asset_id = prepared_context.params['asset_id']

    try:
        conviso_api = flow_context.create_conviso_api_client_beta()
        LOGGER.info("💬 Starting the import process for the SARIF file.")
        parse_sarif_file(conviso_api, asset_id, input_file)
    except Exception as e:
        LOGGER.error(f"❌ Error during SARIF file import: {str(e)}")
        raise Exception("SARIF file import failed. Please contact support and provide the SARIF file for assistance.")


def parse_sarif_file(conviso_api, asset_id, sarif_file):
    try:
        sarif_data = _load_sarif_data(sarif_file)
        if not sarif_data:
            raise Exception("Failed to load SARIF file")

        sarif_infos = _extract_rules_info(sarif_data)

        success_count = 0
        error_count = 0

        for run in sarif_data.get('runs', []):
            for result in run.get('results', []):
                try:
                    if _process_vulnerability(conviso_api, asset_id, result, sarif_infos):
                        success_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    LOGGER.error(f"❌ Error processing vulnerability: {str(e)}")
                    error_count += 1

        LOGGER.info(f"✅ Successfully processed {success_count} vulnerabilities")
        if error_count > 0:
            LOGGER.warning(f"⚠️ {error_count} vulnerabilities with errors")

        LOGGER.info("✅ SARIF file import completed successfully.")

    except Exception as e:
        LOGGER.error(f"❌ Error during SARIF file parsing: {str(e)}")
        raise


def _load_sarif_data(sarif_file):
    try:
        cleaned_file = clean_file(sarif_file)

        with open(cleaned_file, 'r', encoding='utf-8') as file:
            sarif_data = json.load(file)

        if not isinstance(sarif_data, dict) or 'runs' not in sarif_data:
            LOGGER.error("❌ Invalid SARIF file: 'runs' structure not found")
            return None

        return sarif_data

    except json.JSONDecodeError as e:
        LOGGER.error(f"❌ Error decoding JSON: {str(e)}")
        return None
    except Exception as e:
        LOGGER.error(f"❌ Error loading file: {str(e)}")
        return None


def _extract_rules_info(sarif_data):
    sarif_infos = []

    for run in sarif_data.get('runs', []):
        for rule in run.get('tool', {}).get('driver', {}).get('rules', []):
            title = (rule.get('shortDescription', {}).get('text') or
                     rule.get('name') or
                     rule.get('fullDescription', {}).get('text') or
                     rule.get('help', {}).get('text'))

            rule_info = {
                "id": rule.get('id'),
                "name": title,
                "references": rule.get('helpUri'),
                "description": _get_rule_description(rule)
            }
            sarif_infos.append(rule_info)

    return sarif_infos


def _get_rule_description(rule):
    return (rule.get('help', {}).get('text') or
            rule.get('fullDescription', {}).get('text') or
            rule.get('shortDescription', {}).get('text'))


def _process_vulnerability(conviso_api, asset_id, result, sarif_infos):
    try:
        if not result.get('ruleId'):
            LOGGER.warning("⚠️ Result without ruleId, skipping...")
            return False

        vuln_data = _extract_vulnerability_data(result, sarif_infos)
        if not vuln_data:
            LOGGER.warning(f"⚠️ Could not extract data for {result.get('ruleId')}")
            return False

        rule_id = result.get('ruleId', '')

        if "(sca)" in rule_id.lower():
            return _process_sca_vulnerability(conviso_api, asset_id, result, vuln_data)
        elif "(sast)" in rule_id.lower():
            return _process_sast_vulnerability(conviso_api, asset_id, result, vuln_data)
        else:
            return _process_sast_vulnerability(conviso_api, asset_id, result, vuln_data)

    except Exception as e:
        LOGGER.error(f"❌ Error processing vulnerability: {str(e)}")
        return False


def _extract_vulnerability_data(result, sarif_infos):
    try:
        rule_id = result.get('ruleId')
        matching_info = next((info for info in sarif_infos if info['id'] == rule_id), None)
        title = None
        references = None
        description = None

        if matching_info:
            title = matching_info['name']
            references = matching_info['references']
            description = matching_info['description']

        if not title:
            title = result.get('message', {}).get('text', 'No title provided')
        if not description:
            description = result.get('message', {}).get('text', 'No description provided')

        locations = result.get('locations', [])
        if not locations:
            LOGGER.warning(f"⚠️ No location found for {rule_id}")
            return None

        first_location = locations[0]
        physical_location = first_location.get('physicalLocation', {})

        return {
            'title': title,
            'references': references,
            'description': description,
            'severity': result.get('level', 'info'),
            'file_name': physical_location.get('artifactLocation', {}).get('uri'),
            'vulnerable_line': physical_location.get('region', {}).get('startLine'),
            'first_line': physical_location.get('region', {}).get('startLine', 1),
            'code_snippet': physical_location.get('contextRegion', {}).get('snippet', {}).get('text', ''),
        }

    except Exception as e:
        LOGGER.error(f"❌ Error extracting vulnerability data: {str(e)}")
        return None


def _process_sca_vulnerability(conviso_api, asset_id, result, vuln_data):
    try:
        message_text = result.get('message', {}).get('text', '')
        sca_data = _parse_sca_data(message_text)

        if not sca_data:
            LOGGER.warning(f"⚠️ Could not extract SCA data from: {message_text}")
            return False

        create_sca_vulnerabilities(
            conviso_api, asset_id, message_text,
            vuln_data['references'], vuln_data['description'],
            vuln_data['severity'], vuln_data['file_name'],
            vuln_data['first_line'], sca_data['package'],
            sca_data['version'], sca_data['cve']
        )

        return True

    except Exception as e:
        LOGGER.error(f"❌ Error processing SCA vulnerability: {str(e)}")
        return False


def _parse_sca_data(message_text):
    try:
        if ':' not in message_text:
            return None

        package = message_text.split(':')[1].split(' ')[0]
        version = package.split('-')[-1] if '-' in package else 'Unknown'
        cve = 'Unknown'

        if '(' in message_text and ')' in message_text:
            parts = message_text.split(' ')
            for part in parts:
                if part.startswith('(') and part.endswith(')'):
                    cve = part.strip('()')
                    break

        return {
            'package': package,
            'version': version,
            'cve': cve
        }

    except Exception as e:
        LOGGER.error(f"❌ Error parsing SCA data: {str(e)}")
        return None


def _process_sast_vulnerability(conviso_api, asset_id, result, vuln_data):
    try:
        create_sast_vulnerabilities(
            conviso_api, asset_id, vuln_data['title'],
            vuln_data['references'], vuln_data['description'],
            vuln_data['vulnerable_line'], vuln_data['severity'],
            vuln_data['file_name'], vuln_data['code_snippet'],
            vuln_data['first_line'], None
        )

        return True

    except Exception as e:
        LOGGER.error(f"❌ Error processing SAST vulnerability: {str(e)}")
        return False


def create_sast_vulnerabilities(conviso_api, asset_id, *args):
    title, references, description, vulnerable_line, severity, file_name, code_snippet, first_line, cve = args

    issue_model = CreateSastFindingInput(
        asset_id=asset_id,
        file_name=file_name,
        vulnerable_line=vulnerable_line or 0,
        title=title or 'No title provided',
        description=description or 'No description provided',
        severity=severity,
        commit_ref=None,
        deploy_id=None,
        code_snippet=parse_code_snippet(code_snippet),
        reference=parse_conviso_references(references),
        first_line=first_line,
        category=None,
        original_issue_id_from_tool=None,
        solution=None
    )

    try:
        conviso_api.issues.create_sast(issue_model)
        LOGGER.debug(f"✅ SAST vulnerability created: {title}")
    except ResponseError as error:
        if error.code == 'RECORD_NOT_UNIQUE':
            LOGGER.debug(f"ℹ️ SAST vulnerability already exists: {title}")
        else:
            LOGGER.error(f"❌ Error creating SAST vulnerability: {error}")
            raise
    except Exception as e:
        LOGGER.error(f"❌ Unexpected error creating SAST vulnerability: {str(e)}")
        raise


def create_sca_vulnerabilities(conviso_api, asset_id, *args):
    title, references, description, severity, file_name, first_line, package, version, cve = args

    issue_model = CreateScaFindingInput(
        asset_id=asset_id,
        title=title,
        description=description,
        severity=severity,
        solution="Update to the last package version.",
        reference=references,
        file_name=file_name,
        affected_version=version,
        package=package,
        cve=cve,
        patched_version='',
        category='',
        original_issue_id_from_tool=''
    )

    try:
        conviso_api.issues.create_sca(issue_model)
        LOGGER.debug(f"✅ SCA vulnerability created: {title}")
    except ResponseError as error:
        if error.code == 'RECORD_NOT_UNIQUE':
            LOGGER.debug(f"ℹ️ SCA vulnerability already exists: {title}")
        else:
            LOGGER.error(f"❌ Error creating SCA vulnerability: {error}")
            raise
    except Exception as e:
        LOGGER.error(f"❌ Unexpected error creating SCA vulnerability: {str(e)}")
        raise


def parse_code_snippet(code_snippet):
    try:
        decoded_text = b64decode(code_snippet).decode("utf-8")
        lines = decoded_text.split("\n")
        cleaned_lines = []

        for line in lines:
            cleaned_line = line.split(": ", 1)[-1]
            cleaned_lines.append(cleaned_line)

        code_snippet = "\n".join(cleaned_lines)

        return code_snippet
    except Exception:
        return code_snippet


def parse_conviso_references(references=[]):
    if not references:
        return ""

    DIVIDER = "\n"

    references_to_join = []

    for reference in references:
        if reference:
            references_to_join.append(reference)

    return DIVIDER.join(references_to_join)


def parse_first_line_number(encoded_base64):
    decoded_text = b64decode(encoded_base64).decode("utf-8")

    regex = r"^(\d+):"

    result = regex_search(regex, decoded_text)

    if result and result.group(1):
        return result.group(1)

    LINE_NUMBER_WHEN_NOT_FOUND = 1
    return LINE_NUMBER_WHEN_NOT_FOUND


def clean_file(input_file):
    with open(input_file, mode="rb") as file:
        content = file.read()

    if content.startswith(b'\xef\xbb\xbf'):
        content = content[3:]

    cleaned_file = input_file + ".cleaned"
    with open(cleaned_file, mode="wb") as file:
        file.write(content)

    return cleaned_file


import_sarif.epilog = '''
'''
EPILOG = '''
Examples:

  \b
  1 - Import results on SARIF file to Conviso Platform:
    $ export CONVISO_API_KEY='your-api-key'
    $ {command} --input-file /path/to/file.sarif

'''  # noqa: E501

SHORT_HELP = "Perform import of vulnerabilities from SARIF file to Conviso Platform"

command = 'conviso findings import-sarif'
import_sarif.short_help = SHORT_HELP
import_sarif.epilog = EPILOG.format(
    command=command,
)
