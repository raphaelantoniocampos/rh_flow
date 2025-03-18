#!/usr/bin/env python3
from rich.logging import RichHandler
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler()])

log = logging.getLogger("rich")

log.info("This is an info message")
log.warning("This is a warning")
log.error("This is an error")
