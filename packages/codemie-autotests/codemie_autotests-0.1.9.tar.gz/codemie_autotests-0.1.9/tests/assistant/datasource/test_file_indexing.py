import pytest

from hamcrest import (
    assert_that,
    equal_to,
)
from requests import HTTPError

from tests.utils.base_utils import get_random_name, assert_response
from tests.test_data.file_indexing_test_data import (
    file_indexing_test_data,
    large_files_test_data,
    RESPONSE_FOR_TWO_FILES,
)
from tests.test_data.index_test_data import index_test_data
from tests.utils.constants import FILES_PATH
from tests.conftest import get_client
from tests.utils.pytest_utils import check_mark


def pytest_generate_tests(metafunc):
    if "embeddings_model" in metafunc.fixturenames:
        is_smoke = check_mark(metafunc, "smoke")
        if is_smoke:
            all_models = get_client().llms.list_embeddings()
            models = [model.base_name for model in all_models]
        else:
            models = index_test_data

        metafunc.parametrize("embeddings_model", models)


@pytest.mark.regression
@pytest.mark.smoke
@pytest.mark.parametrize(
    "file_name,display_name,expected_response",
    file_indexing_test_data,
    ids=[f"{row[0]}" for row in file_indexing_test_data],
)
def test_create_assistant_with_file_datasource(
    assistant,
    assistant_utils,
    datasource_utils,
    embeddings_model,
    similarity_check,
    kb_context,
    file_name,
    display_name,
    expected_response,
):
    datasource = datasource_utils.create_file_datasource(
        name=get_random_name(),
        description=f"[Autotest] {display_name} with {embeddings_model} embedding model",
        files=[str(FILES_PATH / file_name)],
        embeddings_model=embeddings_model,
    )

    test_assistant = assistant(context=kb_context(datasource))

    prompt = "Show KB context. Return all information available in the context. Query may be 'Show content of the KB'"
    response = assistant_utils.ask_assistant(test_assistant, prompt)

    similarity_check.check_similarity(
        response, expected_response, assistant_name=test_assistant.name
    )


@pytest.mark.regression
@pytest.mark.smoke
def test_edit_description_for_file_datasource(datasource_utils):
    initial_description = "[Autotest] Initial CSV datasource description"

    datasource = datasource_utils.create_file_datasource(
        name=get_random_name(),
        description=initial_description,
        files=[str(FILES_PATH / "test.csv")],
    )

    assert_that(datasource.description, equal_to(initial_description))

    updated_description = (
        "[Autotest] Updated CSV datasource description with new details"
    )
    updated_datasource = datasource_utils.update_file_datasource(
        datasource.id, name=datasource.name, description=updated_description
    )
    assert_that(updated_datasource.description, equal_to(updated_description))


@pytest.mark.regression
@pytest.mark.smoke
def test_create_file_datasource_with_unsupported_file(datasource_utils):
    try:
        datasource_utils.create_file_datasource(
            name=get_random_name(),
            description="[Autotest] Test datasource with unsupported video-file.mp4",
            files=[str(FILES_PATH / "video-file.mp4")],
        )
        raise AssertionError("There is no error for unsupported files")
    except HTTPError as e:
        assert_response(
            e.response,
            422,
            "File type must one of pdf, txt, csv, xml, json, yaml, yml, pptx",
        )


@pytest.mark.regression
@pytest.mark.smoke
@pytest.mark.parametrize("file_name", large_files_test_data)
def test_create_file_datasource_with_large_files(datasource_utils, file_name):
    try:
        datasource_utils.create_file_datasource(
            name=get_random_name(),
            description="[Autotest] Test datasource with unsupported video-file.mp4",
            files=[str(FILES_PATH / "large-files" / file_name)],
        )
        raise AssertionError("There is no error for large files")
    except HTTPError as e:
        assert_response(
            e.response, 422, "File too large. Maximum size is 52428800 bytes"
        )


@pytest.mark.regression
@pytest.mark.smoke
def test_create_file_datasource_with_big_number_of_files(datasource_utils):
    files = [str(FILES_PATH / "test.txt") for _ in range(11)]

    try:
        datasource_utils.create_file_datasource(
            name=get_random_name(),
            description="[Autotest] Test datasource with unsupported video-file.mp4",
            files=files,
        )
        raise AssertionError("There is no error for large files")
    except HTTPError as e:
        assert_response(e.response, 422, "Too many files. Maximum count is 10")


@pytest.mark.regression
@pytest.mark.smoke
def test_create_file_datasource_with_two_files(
    assistant, assistant_utils, datasource_utils, kb_context, similarity_check
):
    csv_path = FILES_PATH / "test.csv"
    json_path = FILES_PATH / "test.json"

    datasource = datasource_utils.create_file_datasource(
        name=get_random_name(),
        description="[Autotest] Test datasource with two files",
        files=[str(csv_path), str(json_path)],
    )

    test_assistant = assistant(context=kb_context(datasource))

    response = assistant_utils.ask_assistant(
        test_assistant, "What types of data do we have available?"
    )

    similarity_check.check_similarity(response, RESPONSE_FOR_TWO_FILES)
