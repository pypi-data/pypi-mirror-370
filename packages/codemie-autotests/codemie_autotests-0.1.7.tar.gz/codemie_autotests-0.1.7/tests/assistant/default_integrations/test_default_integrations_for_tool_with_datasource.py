import os

import pytest

from codemie_sdk.models.integration import (
    CredentialTypes,
    IntegrationType,
)
from tests import PROJECT
from tests.assistant.default_integrations import integrations
from tests.enums.tools import Toolkit, GitTool
from tests.test_data.git_tools_test_data import (
    list_branches_set_active_branch_test_data,
)
from tests.utils.aws_parameters_store import CredentialsUtil
from tests.utils.constants import test_project_name

pytestmark = pytest.mark.skipif(
    os.getenv("ENV") == "local", reason="Skipping this test on local environment"
)

git_tool_prompt = list_branches_set_active_branch_test_data[0][2]
git_tool_answer = list_branches_set_active_branch_test_data[0][3]


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
    datasource_utils,
    default_embedding_llm,
    gitlab_datasource,
    code_context,
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
            integration_type, CredentialTypes.GIT, test_project_name
        )

    _git_integration = integration_utils.create_user_integration(
        CredentialTypes.GIT, CredentialsUtil.gitlab_credentials(), test_project_name
    )

    # create a new datasource
    git_datasource = datasource_utils.create_gitlab_datasource(
        setting_id=_git_integration.id,
        embeddings_model=default_embedding_llm.base_name,
        project_name=test_project_name,
    )

    if is_global:
        integration_utils.create_global_integration(
            CredentialTypes.GIT,
            CredentialsUtil.invalid_git_credentials(),
            test_project_name,
        )

    if project_integration:
        integration_utils.create_project_integration(
            CredentialTypes.GIT,
            CredentialsUtil.invalid_git_credentials(),
            test_project_name,
        )

    git_assistant = assistant(
        Toolkit.GIT,
        GitTool.LIST_BRANCHES_IN_REPO,
        context=code_context(git_datasource),
        project_name=test_project_name,
    )

    response = assistant_utils.ask_assistant(git_assistant, git_tool_prompt)

    similarity_check.check_similarity(response, git_tool_answer)


@pytest.mark.regression
@pytest.mark.tescase("EPMCDME-6708")
def test_assistant_with_global_and_project_integration(
    datasource_utils,
    default_embedding_llm,
    code_context,
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
    # Create datasource
    _git_integration = integration_utils.create_global_integration(
        CredentialTypes.GIT, CredentialsUtil.gitlab_credentials(), test_project_name
    )
    git_datasource = datasource_utils.create_gitlab_datasource(
        setting_id=_git_integration.id,
        embeddings_model=default_embedding_llm.base_name,
        project_name=test_project_name,
    )

    # Delete all integrations of type GIT
    for integration_type in IntegrationType:
        integration_utils.delete_integrations_by_type(
            integration_type, CredentialTypes.GIT, test_project_name
        )

    # Create only global (valid) and project (invalid) integrations.
    # Global integration is created in project which is different from the project of the assistant.
    _git_integration = integration_utils.create_global_integration(
        CredentialTypes.GIT, CredentialsUtil.gitlab_credentials(), PROJECT
    )

    integration_utils.create_project_integration(
        CredentialTypes.GIT,
        CredentialsUtil.invalid_git_credentials(),
        test_project_name,
    )

    git_assistant = assistant(
        Toolkit.GIT,
        GitTool.LIST_BRANCHES_IN_REPO,
        context=code_context(git_datasource),
        project_name=test_project_name,
    )

    response = assistant_utils.ask_assistant(git_assistant, git_tool_prompt)

    similarity_check.check_similarity(response, git_tool_answer)


@pytest.mark.regression
@pytest.mark.tescase("EPMCDME-6708")
def test_assistant_with_project_integration_only(
    datasource_utils,
    default_embedding_llm,
    code_context,
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
            integration_type, CredentialTypes.GIT, test_project_name
        )

    # Create project integration only
    _git_integration = integration_utils.create_project_integration(
        CredentialTypes.GIT, CredentialsUtil.gitlab_credentials(), test_project_name
    )

    # create a new datasource
    git_datasource = datasource_utils.create_gitlab_datasource(
        setting_id=_git_integration.id,
        embeddings_model=default_embedding_llm.base_name,
        project_name=test_project_name,
    )

    git_assistant = assistant(
        Toolkit.GIT,
        GitTool.LIST_BRANCHES_IN_REPO,
        context=code_context(git_datasource),
        project_name=test_project_name,
    )

    response = assistant_utils.ask_assistant(git_assistant, git_tool_prompt)

    similarity_check.check_similarity(response, git_tool_answer)
