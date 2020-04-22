import random
import logging

import numpy as np
from environs import Env
from discord.ext.commands import Bot, Cog, command, group

logger = logging.getLogger('Rollo')

class Rollo(Bot):

    def __init__(self, command_prefix, description=None, **options):
        super().__init__(command_prefix, description=description, **options)


class General(Cog): 
    """ General functions """

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.history: dict = {}


    @command()
    async def ping(self, ctx):
        """ Ping the bot """
        await ctx.send('pong')


    @command(aliases=['r'])
    async def roll(self, ctx, dice: str):
        """Rolls a dice in NdN format, depending on prefix: !, ?, ->. (Alt command: r)"""
        if ctx.prefix == '!':
            await General.ro(ctx, dice, self.history)
        elif ctx.prefix == '?':
            await General.rh(ctx, dice, self.history)
        elif ctx.prefix == '->':
            await General.rp(ctx, dice, self.history)


    @command(aliases=['s'])
    async def show(self, ctx):
        """ Show the last thrown dice, even hidden ones. (Alt command: s) """
        guild = ctx.guild if ctx.guild else 'default'
        roll = self.history.get(guild, None)
        if roll is None:
            await ctx.send('Nobody rolled yet')
        else:
            result = ', '.join(map(str, roll))
            await ctx.send(result)


    @command()
    async def choose(self, ctx, *choices: str):
        """Choose between multiple choices."""
        await ctx.send(random.choice(choices))

    @staticmethod
    async def ro(ctx, dice: str, history: dict):
        """ Roll a dice in NdN format openly """
        logger.debug("Rolling open")
        result = await General._r(ctx, dice, history)
        if not result: 
            return 
        await ctx.send(result)


    @staticmethod
    async def rh(ctx, dice: str, history: dict):
        """ Roll a dice in NdN format hidden (PM) """
        logger.debug("Rolling hidden")
        result = await General._r(ctx, dice, history)
        if not result: 
            return 
        await ctx.send(f'{ctx.message.author.mention} rolled hidden!')
        await ctx.message.author.send(result)


    @staticmethod
    async def rp(ctx, dice: str, history: dict):
        """ Roll a dice in NdN format hidden, no info is shown """
        logger.debug("Rolled and passed")
        result = await General._r(ctx, dice, history)
        if not result: 
            return 
        await ctx.send(f'{ctx.message.author.mention} rolled hidden and passed on!')


    @staticmethod
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




class Meiern(Cog): 
    """ Functions to play Meiern """

    def __init__(self):
        super().__init__()
        self.history = {}


    @group(aliases=['m'])
    async def meier(self, ctx):
        """ Roll two hidden d6. Result is stored in extra history (Alt command: m) """
        if ctx.invoked_subcommand is None:
            await General.rh(ctx, '2d6', self.history)


    @meier.command(aliases=['h'])
    async def hoeher(self, ctx):
        """ Roll two hidden d6 and pass on. (Alt command: h) """
        await General.rp(ctx, '2d6', self.history)


    @meier.command(aliases=['z'])
    async def zeig(self, ctx):
        """ Show the last thrown dice in the round. (Alt command: z)"""
        guild = ctx.guild if ctx.guild else 'default'
        roll = self.history.get(guild, None)
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
