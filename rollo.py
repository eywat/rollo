""" Entry point for rollo the Discord bot. The main bot class is defined here as well """

import asyncio
import logging
import random
from typing import Dict, List, Optional, Tuple, Union

import aiohttp
import numpy as np
from discord import Guild
from discord.errors import PrivilegedIntentsRequired
from discord.ext.commands import Bot, Cog, Context, command
from discord.flags import Intents
from environs import Env

from dice import Meiern, _show, rh, ro, rp
from memes import Memes
from util import LOGGER, setup_logger
from vote import Vote


class Rollo(Bot):
    """ Bot class all, here the overall Bot state is managed. """

    def __init__(
        self,
        command_prefix: Union[Tuple[str, ...], str, None] = ("!", "?", "->"),
        description: Optional[str] = None,
        **options,
    ):
        super().__init__(
            command_prefix=command_prefix, description=description, **options
        )


class General(Cog):
    """ General functions """

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot
        self.history: Dict[Union[str, Guild], np.ndarray] = {}
        self.votes: dict = {}

    @command()
    async def ping(self, ctx: Context):
        """ Ping the bot """
        await ctx.send("pong")

    @command(aliases=["r"])
    async def roll(self, ctx: Context, dice: str):
        """Rolls a dice in NdN format, depending on prefix: !, ?, ->. (Alt command: r)"""
        if ctx.prefix == "?":
            await rh(ctx, dice, self.history)
        elif ctx.prefix == "->":
            await rp(ctx, dice, self.history)
        else:
            await ro(ctx, dice, self.history)

    @command(aliases=["s"])
    async def show(self, ctx: Context):
        """ Show the last thrown dice, even hidden ones. (Alt command: s) """
        await _show(ctx, self.history)

    @command(aliases=["c"])
    async def choose(self, ctx: Context, *choices: str):
        """Choose between multiple choices. (Alt command: c)"""
        if not choices:
            try:
                members = [member async for member in ctx.guild.fetch_members(limit=None)]
            except PrivilegedIntentsRequired:
                logging.warning("Privileged intents are required")
                await ctx.send("I can't decide *_*. (Some privileges are not enabled for this bot)")
                return
            logging.debug("Guild members: %s", ', '.join(map(lambda m: m.name, members)))
            member = random.choice(members)
            await ctx.send(member.mention)
        else:
            await ctx.send(random.choice(choices))

    @command(aliases=["v"])
    async def vote(self, ctx: Context, *choices: str, time=20):
        """ Create a vote. (Alt command: v) """
        # Check if voting is possible
        guild = ctx.guild
        if ctx.guild is None:
            await ctx.send("This feature is only supported in guilds")
            return
        vote = self.votes.get(guild)
        if vote:
            await ctx.send("There is already a vote running")
            return

        # Attach a number to each choice
        choice_enum: List[Tuple[int, str]] = list(
            enumerate(map(lambda choice: choice.strip(" ,\n").lower(), choices), 1)
        )
        vote = Vote(self.bot, guild, choice_enum)
        self.votes[guild] = vote
        LOGGER.debug("Started voting listener")
        self.bot.add_listener(vote.on_vote, name="on_message")
        choice_text = (
            "\n".join(
                map(lambda choice: f"{choice[0]}\t\u21D2 \t{choice[1]}", choice_enum)
            )
            if choice_enum
            else "Open voting"
        )
        await ctx.send(f"Voting started for {time}s.\n{choice_text}")

        await asyncio.sleep(time)

        self.bot.remove_listener(vote.on_vote, name="on_message")
        LOGGER.debug("Removed voting listener")
        results = vote.format_results()
        hist = vote.termogram()
        if hist is not None:
            await ctx.send(f"Voting finished!\n{hist}")
        else:
            await ctx.send(f"Voting finished!\n{results}")
        del self.votes[guild]


def create_bot(env: Env, session: aiohttp.ClientSession) -> Bot:
    """ Setup the Bot """
    intents = Intents.default()
    intents.members = True

    bot = Rollo(("!", "?", "->"), intents=intents)

    async def on_ready():
        LOGGER.info("Logged in as %s: %d", bot.user.name, bot.user.id)

    async def on_command_error(_, error):
        LOGGER.warning("Command error: %s", error)

    bot.add_listener(on_ready, "on_ready")
    bot.add_listener(on_command_error, "on_command_error")
    bot.add_cog(General(bot))
    bot.add_cog(Meiern())
    if env.str("TENOR_TOKEN", None) is not None:
        LOGGER.info("Tenor API Key found. Enabling GIF posting!")
        bot.add_cog(Memes(session, env.str("TENOR_TOKEN")))

    return bot


async def main():
    """ Main function """
    env = Env()
    env.read_env()
    setup_logger(env.int("LOG_LEVEL", logging.INFO), env.path("LOG_FILE", None))

    async with aiohttp.ClientSession() as session:
        bot = create_bot(env, session)

        LOGGER.debug("Starting bot")
        await bot.start(env.str("BOT_TOKEN"))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        logging.shutdown()
