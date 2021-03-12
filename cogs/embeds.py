#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
from discord.ext import commands
from cogs import utility
from globals import *


class MessageEmbeds(commands.Cog, name="Embeds"):
    """Make iAxX say the REEEEE word by sometimes sending getting around his
    Adam block."""

    def __init__(self, bot):
        """Initialize the MessageEmbeds commands.
        Parameters
        ----------
        bot: discord.ext.commands.Bot
            The discord bot."""
        self.bot = bot

    # Commands -----------------------------------------------------------------

    @commands.command(description="Post a picture of Adam being fed some grapes.", hidden=True)
    @commands.cooldown(TIMES_B4_COOLDOWN, COOLDOWN_TIME_STANDARD, commands.BucketType.user)
    async def grapes(self, ctx):
        """Sends a picture of Adam being fed grapes by Billy to the chat."""

        await ctx.send(
            "https://scontent-lhr8-1.xx.fbcdn.net/v/t31.0-8/13653389_1782293768722510_3403034873347958592_o.jpg?_nc_cat"
            "=109&ccb=3&_nc_sid=9267fe&_nc_ohc=vN2Rv1jUi_QAX81MuK_&_nc_ht=scontent-lhr8-1.xx&oh=c444d3f22032beaf7e588fb"
            "e5aebd534&oe=60634875"
        )

    @commands.command(description="Post a picture given a URL")
    @commands.cooldown(1, COOLDOWN_TIME_10_MIN, commands.BucketType.user)
    async def picture(self, ctx, url=None):
        """Send a link to a picture in the channel. This will only work 25% of
        the time and otherwise will send a message to the channel.
        Parameters
        ----------
        url: str
            The URL to the picture. Must end in .png, .jpg or .gif."""

        if ctx.author.id != ID_ABUSED:
            await ctx.send("I'm going to ignore that...")
            return

        if url is None or url.startswith("http") is False or url[-4:] not in [".jpg", ".png", ".gif"]:
            await ctx.send(
                "Please provide a URL to an image next time you try to use this command, vile {}."
                .format(utility.get_badword())
            )
            return

        xi = np.random.rand()

        if xi < 0.05:
            await ctx.send(
                "https://scontent-lhr8-1.xx.fbcdn.net/v/t31.0-8/13653389_1782293768722510_3403034873347958592_o.jpg?_nc"
                "_cat=109&ccb=3&_nc_sid=9267fe&_nc_ohc=vN2Rv1jUi_QAX81MuK_&_nc_ht=scontent-lhr8-1.xx&oh=c444d3f22032bea"
                "f7e588fbe5aebd534&oe=60634875"
            )
        elif xi < 0.25:
            await ctx.send(url)
        else:
            utility.log(ctx.guild.name, "Adam wanted to send this picture to chat: " + url)
            await ctx.send("Haha good picture, Adam!")
