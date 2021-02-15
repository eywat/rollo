""" Memes Cog definition """

from functools import partial
from typing import Optional

import aiohttp
from discord.ext.commands import Cog, Context, group

from util import LOGGER, build_query, get


class Memes(Cog):
    def __init__(self, session: aiohttp.ClientSession, token: str):
        super().__init__()
        self._build_query = partial(build_query, "https://api.tenor.com/v1", key=token)
        self.get = partial(get, session)
        self.responses = {"search": {}, "random": {}, "trending": []}

    async def request(
        self, command: str, q: Optional[str] = None, limit: int = 50, **kwargs
    ):
        """ Send a request to tenor with query q for command """
        if command == "trending":
            cache = self.responses[command]
        elif q is None:
            raise ValueError(f"For {command} the query parameter q has to be set!")
        else:
            cache = self.responses[command].get(q, [])
        if cache:
            return cache.pop(0)

        LOGGER.debug(
            "Sendind %s request with following argumens: q=%s, %s",
            command,
            q,
            ",".join([f"{k}={v}" for k, v in kwargs.items()]),
        )

        query = self._build_query(command, q=q, limit=limit, **kwargs)
        response = await self.get(query)
        LOGGER.debug("Request successful")

        results = [result["url"] for result in response["results"]]
        meme = results.pop(0)

        if command == "trending":
            self.responses[command] = results
        else:
            self.responses[command][q] = results

        return meme

    @group()
    async def memes(self, ctx: Context):
        """ Spicy hot memes. """
        if ctx.invoked_subcommand is None:
            await self.search(ctx, "minion")

    @memes.command(aliases=["s"])
    async def search(self, ctx: Context, term: str):
        """ Returns 1 of the 50 most popular memes for search term. (Alt command: s)"""
        try:
            meme = await self.request("search", q=term, limit=50)
        except Exception as e:
            LOGGER.warning("Meme search unsuccessful: %s", str(e))
            meme = "Something went wrong ;_;"
        await ctx.send(meme)

    @memes.command(aliases=["r"])
    async def random(self, ctx: Context, term: str):
        """ Returns 1 random meme for search term. (Alt command: r) """
        try:
            meme = await self.request("random", q=term, limit=50)
        except Exception as e:
            LOGGER.warning("Random meme search unsuccessful: %s", str(e))
            meme = "Something went wrong ;_;"
        await ctx.send(meme)

    @memes.command(aliases=["t"])
    async def trending(self, ctx: Context):
        """ Returns one of the top 50 trending gifs. (Alt command: t) """
        try:
            meme = await self.request("trending", limit=50)
        except Exception as e:
            LOGGER.warning("Trending request unsuccesful: %s", str(e))
            meme = "Something went wrong ;_;"
        await ctx.send(meme)
