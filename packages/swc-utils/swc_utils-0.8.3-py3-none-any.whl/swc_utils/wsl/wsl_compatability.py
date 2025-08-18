from ..tools.config import Config


def get_wsl_path(config: Config, path: str) -> str:
    """
    Convert a windows path to a WSL path if WSL is enabled
    :param config: Application configuration object
    :param path: Windows path
    :return: WSL path
    """
    if not config.get_bool("USE_WSL", False):
        return path

    path_parts = path.split(":\\")
    return f"/mnt/{path_parts[0].lower()}/" + path_parts[1].replace('\\', '/')


def make_wsl_command(config: Config, command: list) -> list:
    """
    Convert a command to a WSL command if WSL is enabled
    :param config: Application configuration object
    :param command: Command to convert
    :return: WSL command
    """
    if not config.get_bool("USE_WSL", False):
        return command

    dist = config["WSL_DISTRO"]
    return ["wsl", "-d", dist, *command]


def get_local_wsl_temp_dir(config: Config) -> str:
    if not config.get_bool("USE_WSL", False):
        return "/tmp/"

    return f"\\\\wsl.localhost\\{config['WSL_DISTRO']}\\tmp\\"
