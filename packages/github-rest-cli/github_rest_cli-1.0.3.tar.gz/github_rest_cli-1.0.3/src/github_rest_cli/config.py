from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    envvar_prefix="GITHUB",
    settings_files=["../../settings.toml", "../../.secrets.toml"],
    environments=["development", "testing", "production"],
    env_switcher="SET_ENV",
)

# The CLI will not work if the variable
# defined in the Validator class are not defined.
AUTH_TOKEN_VALIDATOR = Validator(
    "AUTH_TOKEN",
    must_exist=True,
    messages={
        "must_exist_true": "Environment variable GITHUB_AUTH_TOKEN is not set. Please set it and try again."
    },
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
