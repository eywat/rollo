from typing import Dict, Union
import numpy as np
from discord import Guild
from discord.ext.commands import Cog, Context, group

from util import LOGGER


class Meiern(Cog):
    """ Functions to play Meiern """

    def __init__(self):
        super().__init__()
        self.history = {}

    @group(aliases=["m"])
    async def meier(self, ctx: Context):
        """ Roll two hidden d6. Result is stored in extra history (Alt command: m) """
        if ctx.invoked_subcommand is None:
            await rh(ctx, "2d6", self.history)

    @meier.command(aliases=["h"])
    async def hoeher(self, ctx: Context):
        """ Roll two hidden d6 and pass on. (Alt command: h) """
        await rp(ctx, "2d6", self.history)

    @meier.command(aliases=["z"])
    async def zeig(self, ctx: Context):
        """ Show the last thrown dice in the round. (Alt command: z)"""
        await _show(ctx, self.history)


async def ro(ctx: Context, dice: str, history: Dict[Union[str, Guild], np.ndarray]):
    """ Roll a dice in NdN format openly """
    LOGGER.debug("Rolling open")
    result = await _r(ctx, dice, history)
    if not result:
        return
    await ctx.send(result)


async def rh(ctx: Context, dice: str, history: Dict[Union[str, Guild], np.ndarray]):
    """ Roll a dice in NdN format hidden (PM) """
    LOGGER.debug("Rolling hidden")
    result = await _r(ctx, dice, history)
    if not result:
        return
    await ctx.send(f"{ctx.message.author.mention} rolled hidden!")
    await ctx.message.author.send(result)


async def rp(ctx: Context, dice: str, history: Dict[Union[str, Guild], np.ndarray]):
    """ Roll a dice in NdN format hidden, no info is shown """
    LOGGER.debug("Rolled and passed")
    result = await _r(ctx, dice, history)
    if not result:
        return
    await ctx.send(f"{ctx.message.author.mention} rolled hidden and passed on!")


async def _r(ctx: Context, dice: str, history: Dict[Union[str, Guild], np.ndarray]):
    try:
        rolls, limit = map(int, dice.split("d"))
    except Exception:
        await ctx.send("Format has to be in NdN!")
        return None
    if rolls > 200 or limit > 200:
        await ctx.send("Pls use smaller numbers '_'")
        return None

    result = np.random.randint(low=1, high=limit + 1, size=rolls)
    result = np.sort(result)[::-1]
    LOGGER.debug(result)
    guild = ctx.guild if ctx.guild else "default"
    LOGGER.debug(guild)
    history[guild] = result
    result = ", ".join(map(str, result))
    return result


async def _show(ctx: Context, history: dict):
    guild = ctx.guild if ctx.guild else "default"
    roll = history.get(guild, None)
    if roll is None:
        await ctx.send("Nobody rolled yet")
    else:
        result = ", ".join(map(str, roll))
        await ctx.send(result)
