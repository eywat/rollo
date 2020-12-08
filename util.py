import logging

import aiohttp

LOGGER = logging.getLogger('Rollo')

def setup_logger(log_level: int):
    global LOGGER
    LOGGER.setLevel(log_level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(formatter)
    LOGGER.addHandler(ch)

    LOGGER.debug("Logging setup")


def build_query(url: str, *args, **kwargs) -> str:
    url = url.strip('/')
    args = map(lambda arg: arg.strip('/'), args)
    kwargs = dict(filter(lambda kv: kv[1] is not None, kwargs.items()))
    url = '/'.join([url, *args]) + '?'
    url += '&'.join([f'{key}={value}' for key, value in kwargs.items()])
    return url
    

async def get(session: aiohttp.ClientSession, url: str) -> dict:
    async with session.get(url) as request: 
        data = await request.json()
    return data