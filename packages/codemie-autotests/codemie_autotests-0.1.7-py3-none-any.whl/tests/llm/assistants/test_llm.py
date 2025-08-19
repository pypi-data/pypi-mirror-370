import os
import pytest
from hamcrest import assert_that, has_item
from tests.enums.model_types import ModelTypes
from tests.test_data.llm_test_data import MODEL_RESPONSES
from tests.conftest import get_client


def prepare_test_data(is_smoke):
    env = os.getenv("ENV")
    test_data = []

    if is_smoke:
        available_models = get_client().llms.list()
        for model in available_models:
            test_data.append(pytest.param(model.base_name))
    else:
        for model_data in MODEL_RESPONSES:
            test_data.append(
                pytest.param(
                    model_data.model_type,
                    marks=pytest.mark.skipif(
                        env not in model_data.environments,
                        reason=f"Skip on non {'/'.join(model_data.environments[:-1])} envs",
                    ),
                )
            )

    return test_data


def pytest_generate_tests(metafunc):
    is_smoke = (
        metafunc.config.getoption("-m") == "smoke"
        if metafunc.config.getoption("-m")
        else False
    )

    if not is_smoke:
        selected_markers = metafunc.config.getoption("-m") or ""
        is_smoke = "smoke" in selected_markers

    if "model_type" in metafunc.fixturenames:
        test_data = prepare_test_data(is_smoke)
        metafunc.parametrize("model_type", test_data)


@pytest.mark.regression
@pytest.mark.smoke
def test_assistant_with_different_models(
    client, assistant_utils, model_type, similarity_check
):
    assert_that(
        [row.base_name for row in client.llms.list()],
        has_item(model_type),
        f"{model_type} is missing in backend response",
    )
    assistant = assistant_utils.create_assistant(model_type)
    response = assistant_utils.ask_assistant(assistant, "Just say one word: 'Hello'")

    if model_type in [ModelTypes.DEEPSEEK_R1, ModelTypes.RLAB_QWQ_32B]:
        response = "\n".join(response.split("\n")[-3:])
    similarity_check.check_similarity(response, "Hello")
