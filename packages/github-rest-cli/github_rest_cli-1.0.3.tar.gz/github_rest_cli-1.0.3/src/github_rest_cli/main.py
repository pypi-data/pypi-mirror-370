import argparse
from github_rest_cli.api import (
    get_repository,
    create_repository,
    delete_repository,
    list_repositories,
    dependabot_security,
    deployment_environment,
)
from importlib.metadata import version
import logging


__version__ = version("github-rest-cli")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def cli():
    """
    Create parsers and subparsers for CLI arguments
    """
    parser = argparse.ArgumentParser(
        description="Python CLI for GitHub REST API",
    )

    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(help="GitHub REST API commands", dest="command")

    # Subparser for "get-repository" function
    get_repo_parser = subparsers.add_parser(
        "get-repo", help="Get a repository's details"
    )
    get_repo_parser.add_argument(
        "-n",
        "--name",
        help="The repository name",
        required=True,
        dest="name",
    )
    get_repo_parser.add_argument(
        "-o", "--org", help="The organization name", required=False, dest="org"
    )
    get_repo_parser.set_defaults(func=get_repository)

    # Subparser for "list-repository" function
    list_repo_parser = subparsers.add_parser(
        "list-repo",
        help="List your repositories",
    )
    list_repo_parser.add_argument(
        "-r",
        "--role",
        required=False,
        dest="role",
        help="List repositories by role",
    )
    list_repo_parser.add_argument(
        "-p",
        "--page",
        required=False,
        default=50,
        type=int,
        dest="page",
        help="The number of results",
    )
    list_repo_parser.add_argument(
        "-s",
        "--sort",
        required=False,
        default="pushed",
        dest="sort",
        help="List repositories sorted by",
    )
    list_repo_parser.set_defaults(func=list_repositories)

    # Subparser for "create-repository" function
    create_repo_parser = subparsers.add_parser(
        "create-repo",
        help="Create a new repository",
    )
    create_repo_parser.add_argument(
        "-n",
        "--name",
        required=True,
        dest="name",
        help="The repository name",
    )
    create_repo_parser.add_argument(
        "-v",
        "--visibility",
        required=False,
        default="public",
        dest="visibility",
        help="Whether the repository is private",
    )
    create_repo_parser.add_argument(
        "-o",
        "--org",
        required=False,
        dest="org",
        help="The organization name",
    )
    create_repo_parser.add_argument(
        "-e",
        "--empty",
        required=False,
        action="store_true",
        dest="empty",
        help="Create an empty repository",
    )
    create_repo_parser.set_defaults(func=create_repository)

    # Subparser for "delete-repository" function
    delete_repo_parser = subparsers.add_parser(
        "delete-repo",
        help="Delete an existing repository",
    )
    delete_repo_parser.add_argument(
        "-n",
        "--name",
        required=True,
        dest="name",
        help="The repository name",
    )
    delete_repo_parser.add_argument(
        "-o",
        "--org",
        required=False,
        dest="org",
        help="The organization name",
    )
    delete_repo_parser.set_defaults(func=delete_repository)

    # Subparser for "dependabot" function
    dependabot_parser = subparsers.add_parser(
        "dependabot",
        help="Manage Dependabot settings",
    )
    dependabot_parser.add_argument(
        "-n",
        "--name",
        required=True,
        dest="name",
        help="The repository name",
    )
    dependabot_parser.add_argument(
        "-o",
        "--org",
        dest="org",
        help="The organization name",
    )
    dependabot_parser.add_argument(
        "--enable",
        required=False,
        action="store_true",
        dest="control",
        help="Enable dependabot security updates",
    )
    dependabot_parser.add_argument(
        "--disable",
        required=False,
        action="store_false",
        dest="control",
        help="Disable dependabot security updates",
    )
    dependabot_parser.set_defaults(func=dependabot_security)

    # Subparser for "deployment-environments" function
    deploy_env_parser = subparsers.add_parser(
        "environment",
        help="Manage deployment environments",
    )
    deploy_env_parser.add_argument(
        "-n",
        "--name",
        required=True,
        dest="name",
        help="The repository name",
    )
    deploy_env_parser.add_argument(
        "-e",
        "--env",
        required=True,
        dest="env",
        help="Deployment environment name",
    )
    deploy_env_parser.add_argument(
        "-o",
        "--org",
        required=False,
        dest="org",
        help="The organization name",
    )
    deploy_env_parser.set_defaults(func=deployment_environment)

    args = parser.parse_args()
    command = args.command

    if hasattr(args, "func"):
        if command == "get-repo":
            args.func(args.name, args.org)
        elif command == "list-repo":
            args.func(args.page, args.sort, args.role)
        elif command == "create-repo":
            args.func(args.name, args.visibility, args.org, args.empty)
        elif command == "delete-repo":
            args.func(args.name, args.org)
        elif command == "dependabot":
            args.func(args.name, args.control, args.org)
        elif command == "environment":
            args.func(args.name, args.env, args.org)
        else:
            return False
    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
