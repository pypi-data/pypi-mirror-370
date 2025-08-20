from pathlib import Path
import platformdirs


APP_NAME = "srtify"


def get_app_dir() -> Path:
    """ Get platform-specific application directory """
    app_dir = Path(platformdirs.user_data_dir(APP_NAME))
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_config_path() -> Path:
    """ Get path to config file """
    return get_app_dir() / "config.json"


def get_prompts_path() -> Path:
    """ Get path to prompts file """
    return get_app_dir() / "prompts.json"