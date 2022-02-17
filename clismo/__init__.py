import logging

import clismo.csre

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

__all__ = ["csre"]

__version__ = "0.2.0"
