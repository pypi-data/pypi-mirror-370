import httpx
import respx

from aci import ACI
from aci.meta_functions import (
    ACIExecuteFunction,
    ACISearchFunctions,
)

from .utils import MOCK_BASE_URL, MOCK_LINKED_ACCOUNT_OWNER_ID


@respx.mock
def test_handle_function_call_search_functions(client: ACI) -> None:
    mock_response = [{"name": "Test Function", "description": "Test Description"}]

    route = respx.get(f"{MOCK_BASE_URL}functions/search").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    response = client.handle_function_call(
        ACISearchFunctions.get_name(),
        {"app_names": ["TEST"], "intent": "search functions"},
        linked_account_owner_id=MOCK_LINKED_ACCOUNT_OWNER_ID,
    )
    assert response == mock_response
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_handle_function_call_meta_function_execution(client: ACI) -> None:
    function_arguments = {
        "function_name": "BRAVE_SEARCH__WEB_SEARCH",
        "function_arguments": {"param1": "value1"},
    }
    mock_response = {"success": True, "data": "string"}
    # note: the function name for mock route here should be function_name in the function_arguments
    route = respx.post(
        f"{MOCK_BASE_URL}functions/{function_arguments['function_name']}/execute"
    ).mock(return_value=httpx.Response(200, json=mock_response))

    response = client.handle_function_call(
        ACIExecuteFunction.get_name(),
        function_arguments,
        linked_account_owner_id=MOCK_LINKED_ACCOUNT_OWNER_ID,
    )
    assert response == mock_response
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_handle_function_call_direct_indexed_function_execution(client: ACI) -> None:
    function_name = "BRAVE_SEARCH__WEB_SEARCH"
    function_arguments = {"query": "test"}
    mock_response = {
        "success": True,
        "data": {"results": [{"title": "Test Result"}], "metadata": None},
    }

    route = respx.post(f"{MOCK_BASE_URL}functions/{function_name}/execute").mock(
        return_value=httpx.Response(200, json=mock_response)
    )
    response = client.handle_function_call(
        function_name,
        function_arguments,
        linked_account_owner_id=MOCK_LINKED_ACCOUNT_OWNER_ID,
    )

    assert response == mock_response
    assert route.call_count == 1, "should not retry"
