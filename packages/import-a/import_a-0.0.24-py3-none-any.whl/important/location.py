from pathlib import Path
import important


def root_dir() -> Path:
    """
    root directory of `important` library
    """
    return Path(important.__file__).parent.absolute()


def conf_dir() -> Path:
    """
    Configuration directory of `important` library
    """
    return root_dir() / "conf"


ROOT_DIR = root_dir()
CONF_DIR = conf_dir()
