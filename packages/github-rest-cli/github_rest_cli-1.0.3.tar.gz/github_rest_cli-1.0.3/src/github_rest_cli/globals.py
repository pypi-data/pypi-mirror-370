from github_rest_cli.config import settings, AUTH_TOKEN_VALIDATOR
from dynaconf.base import ValidationError
import logging


GITHUB_URL = "https://api.github.com"
logger = logging.getLogger(__name__)


def get_headers():
    try:
        AUTH_TOKEN_VALIDATOR.validate(settings)
    except ValidationError as e:
        logger.error(str(e))
        raise SystemExit(1)

    return {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"token {settings.AUTH_TOKEN}",
    }
