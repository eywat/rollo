import random
import logging
import asyncio
from tempfile import TemporaryFile
from collections import OrderedDict

import aiohttp
import discord
from discord.ext.commands import Bot, Cog, Context, group, command

from environs import Env

from dice import Meiern, ro, rp, rh, _show
from memes import Memes
from vote import Vote
from util import LOGGER, setup_logger


class Rollo(Bot):

    def __init__(self, command_prefix, description=None, **options):
        super().__init__(command_prefix, description=description, **options)


class General(Cog):
    """ General functions """

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot
        self.history: dict = {}
        self.votes: dict = {}

    @command()
    async def ping(self, ctx: Context):
        """ Ping the bot """
        await ctx.send('pong')

    @command(aliases=['r'])
    async def roll(self, ctx: Context, dice: str):
        """Rolls a dice in NdN format, depending on prefix: !, ?, ->. (Alt command: r)"""
        if ctx.prefix == '!':
            await ro(ctx, dice, self.history)
        elif ctx.prefix == '?':
            await rh(ctx, dice, self.history)
        elif ctx.prefix == '->':
            await rp(ctx, dice, self.history)

    @command(aliases=['s'])
    async def show(self, ctx: Context):
        """ Show the last thrown dice, even hidden ones. (Alt command: s) """
        await _show(ctx, self.history)

    @command(aliases=['c'])
    async def choose(self, ctx: Context, *choices: str):
        """Choose between multiple choices. (Alt command: c)"""
        await ctx.send(random.choice(choices))

    @command(aliases=['v'])
    async def vote(self, ctx: Context, *choices: str, time=20):
        """ Create a vote. (Alt command: v) """
        guild = ctx.guild
        if not ctx.guild:
            await ctx.send("This feature is only supported in guilds")
        vote = self.votes.get(guild)
        if vote:
            await ctx.send("There is already a vote running")
            return

        choices = list(
            enumerate(
                map(lambda choice: choice.strip(" ,\n").lower(), choices),
                1))
        vote = Vote(self.bot, guild, choices)
        self.votes[guild] = vote
        LOGGER.debug("Started voting listener")
        self.bot.add_listener(vote.on_vote, name='on_message')
        choices = "\n".join(
            map(lambda choice: f"{choice[0]}\t\u21D2 \t{choice[1]}", choices)) if choices else "Open voting"
        await ctx.send(f"Voting started for {time}s.\n{choices}")

        await asyncio.sleep(time)

        self.bot.remove_listener(vote.on_vote, name='on_message')
        LOGGER.debug("Removed voting listener")
        results = vote.format_results()
        hist = vote.histogram()
        if hist:
            with TemporaryFile() as f:
                hist.savefig(f)
                f.flush()
                f.seek(0)
                await ctx.send(f"Voting finished.\n{results}", file=discord.File(f, "results.png"))
        else:
            await ctx.send(f"Voting finished.\n{results}")
        del self.votes[guild]


def create_bot(env: Env, session: aiohttp.ClientSession) -> Bot:
    bot = Rollo(("!", "?", "->"))

    async def on_ready():
        LOGGER.info('Logged in as %s: %d', bot.user.name, bot.user.id)

    async def on_command_error(_, error):
        LOGGER.warning(f"Command error: {error}")

    bot.add_listener(on_ready, 'on_ready')
    bot.add_listener(on_command_error, 'on_command_error')
    bot.add_cog(General(bot))
    bot.add_cog(Meiern())
    if env('TENOR_TOKEN', None):
        bot.add_cog(Memes(session, env('TENOR_TOKEN')))

    return bot


async def main():
    env = Env()
    env.read_env()
    setup_logger(env.int('LOG_LEVEL', logging.INFO))

    async with aiohttp.ClientSession() as session:
        bot = create_bot(env, session)

        LOGGER.debug('Starting bot')
        await bot.start(env('BOT_TOKEN'))


if __name__ == "__main__":
    asyncio.run(main())
