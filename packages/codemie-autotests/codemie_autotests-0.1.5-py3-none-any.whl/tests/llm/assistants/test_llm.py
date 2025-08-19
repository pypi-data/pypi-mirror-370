import pytest
from hamcrest import assert_that, has_item

from tests.enums.model_types import ModelTypes
from tests.test_data.llm_test_data import llm_test_data


@pytest.mark.parametrize(
    "model_type",
    llm_test_data,
    ids=[f"{row[0][0]}" for row in llm_test_data],
)
@pytest.mark.regression
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
