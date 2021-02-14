""" Here voting utilities are defined """

from typing import List, Tuple, Optional

import seaborn as sns
import matplotlib.pyplot as plt
from discord import Guild
from discord.ext.commands import Bot

from util import LOGGER


class Vote:
    def __init__(self, bot: Bot, guild: Guild, choices: List[Tuple[int, str]]):
        self.bot = bot
        self.guild = guild
        self.voters = []
        self.open = not any(choices)
        self.choices = list(map(lambda choice: [*choice, 0], choices))

        LOGGER.debug(self.choices)

    async def on_vote(self, message):
        if message.author == self.bot.user:
            LOGGER.debug("Own message")
            return
        if message.content.startswith(self.bot.command_prefix):
            LOGGER.debug("Detected command")
            return
        if message.author in self.voters:
            LOGGER.debug("Already voted %s", message.author)
            return

        self.voters.append(message.author)
        content = message.content.strip(" ,\n").lower()
        LOGGER.debug(content)
        if self.open:
            choice = list(filter(lambda choice: choice[1] == content, self.choices))
            if choice:
                LOGGER.debug("Incrementing existing choice")
                choice[0][2] += 1
            else:
                LOGGER.debug("Creating new choice")
                self.choices.append([len(self.choices) + 1, content, 1])
            return

        try:
            index = int(content)
            choice = next(filter(lambda choice: choice[0] == index, self.choices))
            LOGGER.debug("Got integer")
            choice[2] += 1
        except:
            try:
                LOGGER.debug("Got name")
                choice = next(filter(lambda choice: choice[1] == content, self.choices))
                choice[2] += 1
            except:
                LOGGER.debug("Not found")
                return

    def format_results(self) -> str:
        return "\n".join(
            map(
                lambda choice: f"{choice[0]}: {choice[1]}\t\u21D2 {choice[2]}",
                self.choices,
            )
        )

    def histogram(self) -> Optional[plt.Figure]:
        x = list(map(lambda choice: choice[1], self.choices))
        y = list(map(lambda choice: choice[2], self.choices))

        if not x or not y:
            return None

        hist = sns.barplot(x, y)
        fig = hist.get_figure()

        return fig
