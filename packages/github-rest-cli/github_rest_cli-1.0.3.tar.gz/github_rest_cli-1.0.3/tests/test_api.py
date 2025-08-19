from github_rest_cli import api


GET_HEADERS_FUNCTION = "github_rest_cli.api.get_headers"
FETCH_USER_FUNCTION = "github_rest_cli.api.fetch_user"
REQUEST_HANDLER_FUNCTION = "github_rest_cli.api.request_with_handling"


def test_fetch_user(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"login": "test-user"}
    mock_response.raise_for_status = lambda: None

    mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=mock_response)

    result = api.fetch_user()

    assert result == "test-user"


def test_create_repository_user(mocker):
    expected_message = "Repository successfully created in test-user/test-repo."

    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")
    mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=expected_message)

    result = api.create_repository("test-repo", "public")

    assert result == expected_message


def test_create_repository_org(mocker):
    expected_message = "Repository successfully created in test-org/test-repo."

    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=expected_message)

    result = api.create_repository("test-repo", "public", "test-org")

    assert result == expected_message
