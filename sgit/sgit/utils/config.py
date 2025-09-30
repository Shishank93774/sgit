import os
import configparser
from typing import Optional


def repo_default_config() -> configparser.ConfigParser:
    """
    Create a default Git repository configuration.

    Returns:
        ConfigParser object with default core settings.
    """
    config = configparser.ConfigParser()
    config.add_section("core")
    config.set("core", "repositoryformatversion", "0")
    config.set("core", "filemode", "false")
    config.set("core", "bare", "false")
    return config


def gitconfig_read() -> configparser.ConfigParser:
    """
    Read the global git configuration from standard locations.

    Returns:
        ConfigParser object containing user/system Git configuration.
    """
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME", "~/.config")
    configfiles = [
        os.path.expanduser(os.path.join(xdg_config_home, "git/config")),
        os.path.expanduser("~/.gitconfig")
    ]
    config = configparser.ConfigParser()
    config.read(configfiles)
    return config


def gitconfig_user_get(config: configparser.ConfigParser) -> Optional[str]:
    """
    Get the user name and email from a Git config.

    Args:
        config: ConfigParser object to read user information from.

    Returns:
        A string in the format "Name <email>", or None if not set.
    """
    if "user" in config:
        if "name" in config["user"] and "email" in config["user"]:
            return f"{config['user']['name']} <{config['user']['email']}>"
    return None