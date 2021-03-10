#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
from discord.ext import commands
from cogs import utility
from globals import *


class Evasion(commands.Cog, name="Utility"):
    """Make iAxX say the REEEEE word by sometimes sending getting around his
    Adam block."""

    @commands.command(description="Post a picture of Adam being fed some grapes.", hidden=True)
    @commands.cooldown(TIMES_B4_COOLDOWN, COOLDOWN_TIME_STANDARD, commands.BucketType.user)
    async def grapes(self, ctx):
        """Sends a picture of Adam being fed grapes by Billy to the chat."""

        await ctx.send(
            "https://scontent-lhr8-1.xx.fbcdn.net/v/t31.0-8/13653389_1782293768722510_3403034873347958592_o.jpg?_nc_cat"
            "=109&ccb=3&_nc_sid=9267fe&_nc_ohc=vN2Rv1jUi_QAX81MuK_&_nc_ht=scontent-lhr8-1.xx&oh=c444d3f22032beaf7e588fb"
            "e5aebd534&oe=60634875"
        )

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Post a picture given a URL")
    @commands.cooldown(TIMES_B4_COOLDOWN, COOLDOWN_TIME_STANDARD, commands.BucketType.user)
    async def picture(self, ctx, url=None):
        """Send a link to a picture in the channel. This will only work 0.001% of
        the time and otherwise will send a message to the channel.
        Parameters
        ----------
        url: str
            The URL to the picture. Must end in .png, .jpg or .gif."""

        if url is None or url[-4:] not in [".jpg", ".png", ".gif"]:
            await ctx.send(
                "Please provide a URL to an image next time you try to use this command, vile {}."
                .format(utility.get_badword())
            )
            return

        xi = np.random.rand()

        if xi < 0.25:
            await ctx.send(url)
        elif xi < 0.01:
            await ctx.send(
                "https://scontent-lhr8-1.xx.fbcdn.net/v/t31.0-8/13653389_1782293768722510_3403034873347958592_o.jpg?_nc"
                "_cat=109&ccb=3&_nc_sid=9267fe&_nc_ohc=vN2Rv1jUi_QAX81MuK_&_nc_ht=scontent-lhr8-1.xx&oh=c444d3f22032bea"
                "f7e588fbe5aebd534&oe=60634875"
            )
        else:
            utility.log(ctx.guild.name, "Adam wanted to send this picture to chat: " + url)
            await ctx.send("Haha good picture, Adam!")
