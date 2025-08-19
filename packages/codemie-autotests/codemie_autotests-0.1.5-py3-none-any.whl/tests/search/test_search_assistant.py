import pytest
from hamcrest import assert_that

from tests import TEST_USER
from tests.utils.base_utils import get_random_name


@pytest.fixture(scope="session")
def test_assistant_name():
    base_name = get_random_name()
    return f"{base_name}_assistant_for_search_test"


@pytest.fixture(scope="session")
def test_assistant_partial_name(test_assistant_name):
    return test_assistant_name[:8]


@pytest.fixture(scope="session", autouse=True)
def assistant(assistant_utils, default_llm, test_assistant_name):
    assistant = assistant_utils.create_assistant(
        assistant_name=test_assistant_name,
        shared=True,
        llm_model_type=default_llm.base_name,
    )
    yield assistant
    if assistant:
        assistant_utils.delete_assistant(assistant)


@pytest.fixture(scope="session")
def test_data(test_assistant_name, test_assistant_partial_name):
    return [
        {"search": test_assistant_name},
        {"created_by": TEST_USER, "search": test_assistant_name},
        {"created_by": TEST_USER},
        {"shared": True, "search": test_assistant_name},
        {"is_global": False, "search": test_assistant_name},
        {"search": test_assistant_partial_name},
        {"created_by": TEST_USER, "search": test_assistant_partial_name},
        {"shared": True, "search": test_assistant_partial_name},
        {"is_global": False, "search": test_assistant_partial_name},
    ]


@pytest.fixture
def filters(request, test_data):
    return test_data[request.param]


def pytest_generate_tests(metafunc):
    if "filters" in metafunc.fixturenames:
        # Parametrize with indices instead of actual data
        metafunc.parametrize(
            "filters",
            list(range(9)),  # 9 test cases
            ids=[
                "search_full_name",
                "created_by_and_search_full",
                "created_by_only",
                "shared_and_search_full",
                "not_global_and_search_full",
                "search_partial_name",
                "created_by_and_search_partial",
                "shared_and_search_partial",
                "not_global_and_search_partial",
            ],
            indirect=True,
        )


@pytest.mark.testcase("EPMCDME-2429, EPMCDME-4102")
@pytest.mark.regression
def test_search_assistant_by_filters(search_utils, filters, test_assistant_name):
    response = search_utils.list_assistants(filters)
    names = list(map(lambda item: item["name"], response))

    assert_that(
        test_assistant_name in names, "Assistant is not found in search results."
    )
