import os
from dataset_up.config import constants
def get_config_dir() -> str:
    return constants.DEFAULT_CONFIG_DIR

def get_version_file_name() -> str:
    return constants.DEFAULT_CLI_VERSION_FILE_NAME


def get_token_file_name() -> str:
    return constants.DEFAULT_CLI_TOKEN_FILE_NAME


def get_config_file_name() -> str:
    return constants.DEFAULT_CLI_CONFIG_FILE_NAME


def get_config_path() -> str:
    return os.path.join(get_config_dir(), get_config_file_name())


def get_token_path() -> str:
    return os.path.join(get_config_dir(), get_token_file_name())


def get_version_path() -> str:
    return os.path.join(get_config_dir(), get_version_file_name())
