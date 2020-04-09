import random
import logging

from environs import Env
from discord.ext import commands

logger = logging.getLogger('Rollo')
bot = commands.Bot(("!", "?", "->"))
history = None


@bot.event
async def on_ready():
    logger.info('Logged in as %s: %d', bot.user.name, bot.user.id)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format, depending on prefix (!, ?, ->)."""
    if ctx.prefix == '!':
        await r(ctx, dice)
    elif ctx.prefix == '?':
        await rh(ctx, dice)
    elif ctx.prefix == '->':
        await rp(ctx, dice)


@bot.command()
async def r(ctx, dice: str):
    """ Roll a dice in NdN format openly """
    logger.debug("Rolling open")
    result = await _r(ctx, dice)
    await ctx.send(result)


@bot.command()
async def rh(ctx, dice: str):
    """ Roll a dice in NdN format hidden (PM) """
    logger.debug("Rolling hidden")
    result = await _r(ctx, dice)
    await ctx.send(f'{ctx.message.author.mention} rolled hidden!')
    await ctx.message.author.send(result)


@bot.command()
async def rp(ctx, dice: str):
    """ Roll a dice in NdN format hidden, no info is shown """
    logger.debug("Rolled and passed")
    result = await _r(ctx, dice)
    await ctx.send(f'{ctx.message.author.mention} rolled hidden and passed on!')


async def _r(ctx, dice: str):
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return
    result = [random.randint(1, limit) for r in range(rolls)]
    result.sort(reverse=True)
    logger.debug(result)
    global history
    history = result
    result = ', '.join(map(str, result))
    return result


@bot.command()
""" Show the last thrown dice (even hidden) """
async def show(ctx):
    global history
    if history == None:
        await ctx.send('Nobody rolled yet')
    else:
        result = ', '.join(map(str, history))
        await ctx.send(result)


@bot.command(description='For when you wanna settle the score some other way')
async def choose(ctx, *choices: str):
    """Choose between multiple choices."""
    await ctx.send(random.choice(choices))


@bot.group()
async def meier(ctx):
    """ Roll two hidden d6 """
    if ctx.invoked_subcommand is None:
        await rh(ctx, '2d6')


@meier.command()
async def hoeher(ctx):
    """ Roll two hidden d6 and pass on """
    await rp(ctx, '2d6')


@meier.command()
async def zeig(ctx):
    """ Show the last thrown dice """
    await show(ctx)


def setup_logger(log_level):
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

    logger.info('Starting bot')
    bot.run(env('BOT_TOKEN'))


if __name__ == "__main__":
    main()
