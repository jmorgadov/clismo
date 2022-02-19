import logging

import clismo.csre

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

__all__ = ["csre"]

__version__ = "0.1.1"
