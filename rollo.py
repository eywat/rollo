import random
import logging
import asyncio
from tempfile import TemporaryFile
from collections import OrderedDict

import discord
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from environs import Env
from discord.ext.commands import Bot, Cog, command, group

logger = logging.getLogger('Rollo')


class Rollo(Bot):

    def __init__(self, command_prefix, description=None, **options):
        super().__init__(command_prefix, description=description, **options)


class General(Cog):
    """ General functions """

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot
        self.history: dict = {}
        self.vote: dict = {}

    @command()
    async def ping(self, ctx):
        """ Ping the bot """
        await ctx.send('pong')

    @command(aliases=['r'])
    async def roll(self, ctx, dice: str):
        """Rolls a dice in NdN format, depending on prefix: !, ?, ->. (Alt command: r)"""
        if ctx.prefix == '!':
            await ro(ctx, dice, self.history)
        elif ctx.prefix == '?':
            await rh(ctx, dice, self.history)
        elif ctx.prefix == '->':
            await rp(ctx, dice, self.history)

    @command(aliases=['s'])
    async def show(self, ctx):
        """ Show the last thrown dice, even hidden ones. (Alt command: s) """
        await _show(ctx, self.history)

    @command(aliases=['c'])
    async def choose(self, ctx, *choices: str):
        """Choose between multiple choices. (Alt command: c)"""
        await ctx.send(random.choice(choices))

    @command(aliases=['v'])
    async def vote(self, ctx, *choices: str, time=20):
        """ Create a vote. (Alt command: v) """
        guild = ctx.guild
        if not ctx.guild:
            await ctx.send("This feature is only supported in guilds")
        vote = self.vote.get(guild)
        if vote:
            await ctx.send("There is already a vote running")
            return

        choices = list(
            enumerate(
                map(lambda choice: choice.strip(" ,\n").lower(), choices),
                1))
        vote = Vote(self.bot, guild, choices)
        self.vote[guild] = vote
        logger.debug("Started voting listener")
        self.bot.add_listener(vote.on_vote, name='on_message')
        choices = "\n".join(
            map(lambda choice: f"{choice[0]}\t\u21D2 \t{choice[1]}", choices)) if choices else "Open voting"
        await ctx.send(f"Voting started for {time}s.\n{choices}")

        await asyncio.sleep(time)

        self.bot.remove_listener(vote.on_vote, name='on_message')
        logger.debug("Removed voting listener")
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
        del self.vote[guild]


class Vote:

    def __init__(self, bot: Bot, guild, choices):
        self.bot = bot
        self.guild = guild
        self.voters = []
        self.open = not any(choices)
        self.choices = list(
            map(lambda choice: [*choice, 0], choices))

        logger.debug(self.choices)

    async def on_vote(self, message):
        if message.author == self.bot.user:
            logger.debug("Own message")
            return
        if message.content.startswith(self.bot.command_prefix):
            logger.debug("Detected command")
            return
        if message.author in self.voters:
            logger.debug("Already voted %s", message.author)
            return

        self.voters.append(message.author)
        content = message.content.strip(" ,\n").lower()
        logger.debug(content)
        if self.open:
            choice = list(
                filter(lambda choice: choice[1] == content,
                       self.choices))
            if choice:
                logger.debug("Incrementing existing choice")
                choice[0][2] += 1
            else:
                logger.debug("Creating new choice")
                self.choices.append(
                    [len(self.choices) + 1, content, 1])
            return

        try:
            index = int(content)
            choice = next(
                filter(lambda choice: choice[0] == index, self.choices))
            logger.debug("Got integer")
            choice[2] += 1
        except:
            try:
                logger.debug("Got name")
                choice = next(
                    filter(lambda choice: choice[1] == content, self.choices))
                choice[2] += 1
            except:
                logger.debug("Not found")
                return

    def format_results(self) -> str:
        return "\n".join(
            map(lambda choice: f"{choice[0]}: {choice[1]}\t\u21D2 {choice[2]}",
                self.choices))

    def histogram(self) -> plt.Figure:
        x = list(map(lambda choice: choice[1], self.choices))
        y = list(map(lambda choice: choice[2], self.choices))

        if not x or not y:
            return None

        hist = sns.barplot(x, y)
        fig = hist.get_figure()

        return fig


class Meiern(Cog):
    """ Functions to play Meiern """

    def __init__(self):
        super().__init__()
        self.history = {}

    @group(aliases=['m'])
    async def meier(self, ctx):
        """ Roll two hidden d6. Result is stored in extra history (Alt command: m) """
        if ctx.invoked_subcommand is None:
            await rh(ctx, '2d6', self.history)

    @meier.command(aliases=['h'])
    async def hoeher(self, ctx):
        """ Roll two hidden d6 and pass on. (Alt command: h) """
        await rp(ctx, '2d6', self.history)

    @meier.command(aliases=['z'])
    async def zeig(self, ctx):
        """ Show the last thrown dice in the round. (Alt command: z)"""
        await _show(ctx, self.history)


async def ro(ctx, dice: str, history: dict):
    """ Roll a dice in NdN format openly """
    logger.debug("Rolling open")
    result = await _r(ctx, dice, history)
    if not result:
        return
    await ctx.send(result)


async def rh(ctx, dice: str, history: dict):
    """ Roll a dice in NdN format hidden (PM) """
    logger.debug("Rolling hidden")
    result = await _r(ctx, dice, history)
    if not result:
        return
    await ctx.send(f'{ctx.message.author.mention} rolled hidden!')
    await ctx.message.author.send(result)


async def rp(ctx, dice: str, history: dict):
    """ Roll a dice in NdN format hidden, no info is shown """
    logger.debug("Rolled and passed")
    result = await _r(ctx, dice, history)
    if not result:
        return
    await ctx.send(f'{ctx.message.author.mention} rolled hidden and passed on!')


async def _r(ctx, dice: str, history: dict):
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return None
    if rolls > 200 or limit > 200:
        await ctx.send("Fuck off! Use propper numbers")
        return None

    result = np.random.randint(low=1, high=limit+1, size=rolls)
    result = np.sort(result)[::-1]
    logger.debug(result)
    guild = ctx.guild if ctx.guild else 'default'
    logger.debug(guild)
    history[guild] = result
    result = ', '.join(map(str, result))
    return result


async def _show(ctx, history: dict):
    guild = ctx.guild if ctx.guild else 'default'
    roll = history.get(guild, None)
    if roll is None:
        await ctx.send('Nobody rolled yet')
    else:
        result = ', '.join(map(str, roll))
        await ctx.send(result)


def create_bot() -> Bot:
    bot = Rollo(("!", "?", "->"))

    async def on_ready():
        logger.info('Logged in as %s: %d', bot.user.name, bot.user.id)

    async def on_command_error(ctx, error):
        logger.warning(f"Command error: {error}")

    bot.add_listener(on_ready, 'on_ready')
    bot.add_listener(on_command_error, 'on_command_error')
    bot.add_cog(General(bot))
    bot.add_cog(Meiern())

    return bot


def setup_logger(log_level: int):
    global logger
    logger.setLevel(log_level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.debug("Logging setup")


def main():
    env = Env()
    env.read_env()

    setup_logger(env.int('LOG_LEVEL', logging.INFO))

    bot = create_bot()

    logger.debug('Starting bot')
    bot.run(env('BOT_TOKEN'))


if __name__ == "__main__":
    main()
