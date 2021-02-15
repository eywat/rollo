""" Utility functions """

import logging
from pathlib import Path
from typing import Iterator

import aiohttp

LOGGER = logging.getLogger("Rollo")


def setup_logger(log_level: int, log_file: Path = None):
    """ Setup the global logger. """
    global LOGGER
    LOGGER.setLevel(log_level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    if log_file:
        fh = logging.FileHandler(log_file)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        LOGGER.addHandler(fh)
    else:
        sh = logging.StreamHandler()
        sh.setLevel(log_level)
        sh.setFormatter(formatter)
        LOGGER.addHandler(sh)

    LOGGER.debug("Logging setup")


def build_query(url: str, *args, **kwargs) -> str:
    """Build a query for an url in the style
    `{url}/{arg[0]}/{arg[...]}?{kwarg[0].key}={kwarg[0].value}&{kwarg_n...}`"""
    url = url.strip("/")
    args = map(lambda arg: arg.strip("/"), args)
    kwargs = dict(filter(lambda kv: kv[1] is not None, kwargs.items()))
    url = "/".join([url, *args]) + "?"
    url += "&".join([f"{key}={value}" for key, value in kwargs.items()])
    return url


async def get(session: aiohttp.ClientSession, url: str) -> dict:
    """ Send a get request using the provided ClientSession to url """
    async with session.get(url) as request:
        data = await request.json()
    return data
