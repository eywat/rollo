import random
import logging

from collections import deque

import numpy as np
from environs import Env
from discord.ext.commands import Bot


class Rollo(Bot):

    def __init__(self, command_prefix, description=None, **options):
        super().__init__(command_prefix, description=description, **options)
        self.history = {}
        self.meier_history = {}

logger = logging.getLogger('Rollo')
bot = Rollo(("!", "?", "->"))


@bot.event
async def on_ready():
    logger.info('Logged in as %s: %d', bot.user.name, bot.user.id)


@bot.command()
async def ping(ctx):
    """ Ping the bot """
    await ctx.send('pong')


@bot.command()
async def roll(ctx, dice: str, history: dict = bot.history):
    """Rolls a dice in NdN format, depending on prefix (!, ?, ->)."""
    if ctx.prefix == '!':
        await r(ctx, dice, history)
    elif ctx.prefix == '?':
        await rh(ctx, dice, history)
    elif ctx.prefix == '->':
        await rp(ctx, dice, history)


@bot.command()
async def r(ctx, dice: str, history: dict = bot.history):
    """ Roll a dice in NdN format openly """
    logger.debug("Rolling open")
    result = await _r(ctx, dice, history)
    if not result: 
        return 
    await ctx.send(result)


@bot.command()
async def rh(ctx, dice: str, history: dict = bot.history):
    """ Roll a dice in NdN format hidden (PM) """
    logger.debug("Rolling hidden")
    result = await _r(ctx, dice, history)
    if not result: 
        return 
    await ctx.send(f'{ctx.message.author.mention} rolled hidden!')
    await ctx.message.author.send(result)


@bot.command()
async def rp(ctx, dice: str, history: dict = bot.history):
    """ Roll a dice in NdN format hidden, no info is shown """
    logger.debug("Rolled and passed")
    result = await _r(ctx, dice, history)
    if not result: 
        return 
    await ctx.send(f'{ctx.message.author.mention} rolled hidden and passed on!')


async def _r(ctx, dice: str, history: dict = bot.history):
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


@bot.command()
async def show(ctx, history=bot.history):
    """ Show the last thrown dice (even hidden) """
    guild = ctx.guild if ctx.guild else 'default'
    roll = history.get(guild, None)
    if roll is None:
        await ctx.send('Nobody rolled yet')
    else:
        result = ', '.join(map(str, roll))
        await ctx.send(result)


@bot.command()
async def choose(ctx, *choices: str):
    """Choose between multiple choices."""
    await ctx.send(random.choice(choices))



@bot.group()
async def meier(ctx):
    """ Roll two hidden d6 """
    if ctx.invoked_subcommand is None:
        await rh(ctx, '2d6', bot.meier_history)


@meier.command()
async def hoeher(ctx):
    """ Roll two hidden d6 and pass on """
    
    await rp(ctx, '2d6', bot.meier_history)


@meier.command()
async def zeig(ctx):
    """ Show the last thrown dice """
    await show(ctx, bot.meier_history)


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

    logger.debug('Starting bot')
    bot.run(env('BOT_TOKEN'))


if __name__ == "__main__":
    main()
