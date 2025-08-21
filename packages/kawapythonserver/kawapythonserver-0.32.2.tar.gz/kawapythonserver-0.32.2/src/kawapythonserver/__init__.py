import os
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

min_kywy_version = '0.31.8'

current_file = Path(__file__)
os.environ["PACKAGE_ROOT_PATH"] = str(current_file.parent.parent)


def get_version() -> str:
    try:
        return version("kawapythonserver")
    except PackageNotFoundError:
        return "0.32.2"


__version__ = get_version()
