"""Shared data structures."""
import logging

from rich.logging import RichHandler

FORMAT = "%(message)s"

logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)
_LOG = logging.getLogger()


CSU_URL = "https://wss.csu.org/SelfService/CMSSvcLogInSlim.jsp"
