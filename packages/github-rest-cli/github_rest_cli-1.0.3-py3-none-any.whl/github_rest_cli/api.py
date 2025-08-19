import requests
from github_rest_cli.globals import GITHUB_URL, get_headers
from github_rest_cli.utils import rich_output, rprint


def request_with_handling(
    method, url, success_msg: str = None, error_msg: str = None, **kwargs
):
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        if success_msg:
            rich_output(success_msg)
        else:
            return response
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        if error_msg and status in error_msg:
            rich_output(error_msg[status], format_str="bold red")
        else:
            rich_output(f"Request failed: status code {status}", format_str="bold red")
        return None
    except requests.exceptions.RequestException as e:
        rich_output(f"Request error: {e}", format_str="bold red")
        return None


def build_url(*segments: str) -> str:
    """
    Build an GitHub REST API endpoint

    Example:
      build_url("repos", "org", "repo", "environments", "prod")

    Result:
      https://api.github.com/repos/org/repo/environments/prod
    """
    base = GITHUB_URL.rstrip("/")
    path = "/".join(segment.strip("/") for segment in segments)
    return f"{base}/{path}"


def fetch_user() -> str:
    headers = get_headers()
    url = build_url("user")
    response = request_with_handling("GET", url, headers=headers)
    if response:
        data = response.json()
        return data.get("login")
    return None


def get_repository(name: str, org: str = None):
    owner = org if org else fetch_user()
    headers = get_headers()
    url = build_url("repos", owner, name)

    response = request_with_handling(
        "GET",
        url,
        headers=headers,
        error_msg={
            401: "Unauthorized access. Please check your token or credentials.",
            404: "The requested repository does not exist.",
        },
    )

    if response:
        data = response.json()
        rprint(data)
    return None


def create_repository(name: str, visibility: str, org: str = None, empty: bool = False):
    payload = {
        "name": name,
        "visibility": visibility,
        "auto_init": True,
    }

    if visibility == "private":
        payload["private"] = True

    if empty:
        payload["auto_init"] = False

    owner = org if org else fetch_user()
    headers = get_headers()
    url = build_url("orgs", owner, "repos") if org else build_url("user", "repos")

    return request_with_handling(
        "POST",
        url,
        headers=headers,
        json=payload,
        success_msg=f"Repository successfully created in {owner}/{name}.",
        error_msg={
            401: "Unauthorized access. Please check your token or credentials.",
            422: "Repository name already exists on this account or organization.",
        },
    )


def delete_repository(name: str, org: str = None):
    owner = org if org else fetch_user()
    headers = get_headers()
    url = build_url("repos", owner, name)

    return request_with_handling(
        "DELETE",
        url,
        headers=headers,
        success_msg=f"Repository sucessfully deleted in {owner}/{name}.",
        error_msg={
            403: "The authenticated user does not have sufficient permissions to delete this repository.",
            404: "The requested repository does not exist.",
        },
    )


def list_repositories(page: int, property: str, role: str):
    headers = get_headers()
    url = build_url("user", "repos")

    params = {"per_page": page, "sort": property, "type": role}

    response = request_with_handling(
        "GET",
        url,
        params=params,
        headers=headers,
        error_msg={401: "Unauthorized access. Please check your token or credentials."},
    )

    if response:
        data = response.json()
        repo_full_name = [repo["full_name"] for repo in data]
        for repos in repo_full_name:
            rich_output(f"- {repos}")
        rich_output(f"\nTotal repositories: {len(repo_full_name)}")


def dependabot_security(name: str, enabled: bool, org: str = None):
    is_enabled = bool(enabled)

    owner = org if org else fetch_user()
    headers = get_headers()
    url = build_url("repos", owner, name)
    security_urls = ["vulnerability-alerts", "automated-security-fixes"]

    if is_enabled:
        for endpoint in security_urls:
            full_url = f"{url}/{endpoint}"
            request_with_handling(
                "PUT",
                url=full_url,
                headers=headers,
                success_msg=f"Enabled {endpoint}",
                error_msg={
                    401: "Unauthorized. Please check your credentials.",
                },
            )
    else:
        full_url = f"{url}/{security_urls[0]}"
        request_with_handling(
            "DELETE",
            url=full_url,
            headers=headers,
            success_msg=f"Dependabot has been disabled on repository {owner}/{name}.",
            error_msg={401: "Unauthorized. Please check your credentials."},
        )


def deployment_environment(name: str, env: str, org: str = None):
    owner = org if org else fetch_user()
    headers = get_headers()
    url = build_url("repos", owner, name, "environments", env)

    return request_with_handling(
        "PUT",
        url,
        headers=headers,
        success_msg=f"Environment {env} has been created successfully in {org or owner}/{name}.",
        error_msg={
            422: f"Failed to create repository enviroment {owner or org}/{name}."
        },
    )
