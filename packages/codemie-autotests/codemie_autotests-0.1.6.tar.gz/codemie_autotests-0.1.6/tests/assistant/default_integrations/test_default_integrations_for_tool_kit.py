import os

import pytest

from codemie_sdk.models.integration import (
    CredentialTypes,
    IntegrationType,
)
from tests import PROJECT
from tests.assistant.default_integrations import integrations
from tests.enums.tools import Toolkit, AzureDevOpsWikiTool
from tests.test_data.ado_wiki_tools_test_data import ado_wiki_get_test_data
from tests.utils.aws_parameters_store import CredentialsUtil
from tests.utils.constants import test_project_name

ado_wiki_prompt = ado_wiki_get_test_data[0][2]
ado_wiki_answer = ado_wiki_get_test_data[0][3]

pytestmark = pytest.mark.skipif(
    os.getenv("ENV") == "local", reason="Skipping this test on local environment"
)


@pytest.mark.regression
@pytest.mark.tescase("EPMCDME-6708")
@pytest.mark.parametrize(
    "user_integration, is_global, project_integration",
    integrations,
    ids=[
        f"{row[0].value}-{'global' if row[1] else 'None'}-{row[2].value if row[2] else 'None'}"
        for row in integrations
    ],
)
def test_assistant_should_use_user_integration_by_default(
    integration_utils,
    assistant,
    assistant_utils,
    similarity_check,
    user_integration,
    is_global,
    project_integration,
):
    """
    Test to verify that an assistant should use USER integration by default
    if integration of all types [USER, GLOBAL, PROJECT] are available.
    """

    for integration_type in IntegrationType:
        integration_utils.delete_integrations_by_type(
            integration_type, CredentialTypes.AZURE_DEVOPS, test_project_name
        )

    integration_utils.create_user_integration(
        CredentialTypes.AZURE_DEVOPS,
        CredentialsUtil.azure_devops_credentials(),
        test_project_name,
    )

    if is_global:
        integration_utils.create_global_integration(
            CredentialTypes.AZURE_DEVOPS,
            CredentialsUtil.invalid_ado_credentials(),
            test_project_name,
        )

    if project_integration:
        integration_utils.create_project_integration(
            CredentialTypes.AZURE_DEVOPS,
            CredentialsUtil.invalid_ado_credentials(),
            test_project_name,
        )

    ado_assistant = assistant(
        Toolkit.AZURE_DEVOPS_WIKI,
        AzureDevOpsWikiTool.GET_WIKI,
        project_name=test_project_name,
    )

    response = assistant_utils.ask_assistant(ado_assistant, ado_wiki_prompt)

    similarity_check.check_similarity(response, ado_wiki_answer)


@pytest.mark.regression
@pytest.mark.tescase("EPMCDME-6708")
def test_assistant_with_global_and_project_integration(
    integration_utils,
    assistant,
    assistant_utils,
    similarity_check,
):
    """
    Test to verify that an assistant should use GLOBAL integration if USER integration is not available,
    and both GLOBAL and PROJECT integrations exist.
    GLOBAL integration has valid credentials, PROJECT has invalid.
    """
    for integration_type in IntegrationType:
        integration_utils.delete_integrations_by_type(
            integration_type, CredentialTypes.AZURE_DEVOPS, test_project_name
        )

    # Create only global (valid) and project (invalid) integrations.
    # Global integration is created in project which is different from the project of the assistant.
    integration_utils.create_global_integration(
        CredentialTypes.AZURE_DEVOPS,
        CredentialsUtil.azure_devops_credentials(),
        PROJECT,
    )
    integration_utils.create_project_integration(
        CredentialTypes.AZURE_DEVOPS,
        CredentialsUtil.invalid_ado_credentials(),
        test_project_name,
    )

    ado_assistant = assistant(
        Toolkit.AZURE_DEVOPS_WIKI,
        AzureDevOpsWikiTool.GET_WIKI,
        project_name=test_project_name,
    )

    response = assistant_utils.ask_assistant(ado_assistant, ado_wiki_prompt)

    similarity_check.check_similarity(response, ado_wiki_answer)


@pytest.mark.regression
@pytest.mark.tescase("EPMCDME-6708")
def test_assistant_with_project_integration_only(
    integration_utils,
    assistant,
    assistant_utils,
    similarity_check,
):
    """
    Test to verify that an assistant should use PROJECT integration if it is the only one available.
    """
    for integration_type in IntegrationType:
        integration_utils.delete_integrations_by_type(
            integration_type, CredentialTypes.AZURE_DEVOPS, test_project_name
        )

    # Create project integration only
    integration_utils.create_project_integration(
        CredentialTypes.AZURE_DEVOPS,
        CredentialsUtil.azure_devops_credentials(),
        test_project_name,
    )

    ado_assistant = assistant(
        Toolkit.AZURE_DEVOPS_WIKI,
        AzureDevOpsWikiTool.GET_WIKI,
        project_name=test_project_name,
    )

    response = assistant_utils.ask_assistant(ado_assistant, ado_wiki_prompt)

    similarity_check.check_similarity(response, ado_wiki_answer)
