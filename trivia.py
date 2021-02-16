""" A trivia Cog """

from functools import partial
from typing import Dict, List, Optional, Union
from dataclasses import dataclass

import aiohttp
from discord.ext.commands import Cog, Context, group, Bot
from discord.ext.commands.errors import NoEntryPointError

from rollo import Rollo
from util import LOGGER, build_query, get

@dataclass
class Question:
    question: str
    right_answer: str
    choices: List[str]

class Trivia(Cog):

    def __init__(self, bot: Bot, session: aiohttp.ClientSession) -> None:
        super().__init__()
        self.bot = bot
        self.get = partial(get, session)
        self._build_query = partial(build_query, "https://opentdb.com")
        self._categories = None
    
    @property 
    async def categories(self) -> Dict[int, str]:
        if self._categories:
            return self._categories
        query = self._build_query("api_category.php")
        try:
            cat = await self.get(query)
        except:
            LOGGER.warning("Error fetching category list")
        self._categories = cat


    async def fetch_question(self, category: Union[int, str, None], limit=1) -> Question:
        pass

    @group()
    async def trivia(self, ctx: Context):
        """ Return a trivia question. """
        if ctx.invoked_subcommand is None:
            question = await self.fetch_question(None)

