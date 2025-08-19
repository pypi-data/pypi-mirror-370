import logging
from pathlib import Path

log = logging.getLogger(__name__)


path = Path(__file__)
while not Path.is_dir(path / 'mjaf'):
    path = path.parent

PROJECT_ROOT = path

log.info(f"{PROJECT_ROOT=}")

UTIL_DIR = Path(__file__).parent
