#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""badbot is designed to give human rights back to Adam on the TopGays
discord server and is basically a shitty macbot in some respects."""


import asyncio
import psutil
import atexit
import datetime
import discord
import calendar as c

from discord.ext import commands, tasks
from globals import *
from cogs.chat import SpamBot
from cogs.admin import AdminBot
from cogs.embeds import MessageEmbeds
from cogs import utility

utility.open_logfile()

# The bot itself

SYMBOL = "%"
INTENTS = discord.Intents.default()
INTENTS.members = True
bot = commands.Bot(
    command_prefix=SYMBOL, description="A very stupid Discord bot which can do auto-moderation", intents=INTENTS
)

# Add cogs to bot

bot.add_cog(SpamBot(bot))
bot.add_cog(AdminBot(bot))
bot.add_cog(MessageEmbeds(bot))

# Misc commands ----------------------------------------------------------------


@commands.cooldown(TIMES_B4_COOLDOWN, COOLDOWN_TIME_STANDARD, commands.BucketType.user)
@bot.command(description="Test if the bot is still alive", hidden=True, aliases=["alive"])
async def test(ctx):
    """Send a message if the bot to test if the bot is still alive."""

    process = psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss / 1e9
    await ctx.send(
        "I'm still alive {0.author.name}, and I'm using {1:.1f} GB of memory...".format(ctx, memory_usage)
    )


# Tasks -----------------------------------------------------------------------


@tasks.loop(hours=24)
async def daily_message():
    """Send a message saying how many times 72 abused Adam today. This should
    happen every 24 hours at around midnight. The log file is opened and close
    to indicate a new day."""

    utility.close_logfile()
    utility.open_logfile()

    guild = bot.get_guild(ID_SERVER)
    channel = guild.get_channel(ID_MAIN_CHANNEL)

    n_abuse, n_72 = await utility.count_audit_log(bot.user.id, guild)

    # Construct the update message. This is rather complicated, but the point is
    # to try and have the update message flow naturally for both single and
    # multiple abuses

    message = ":flag_gb::flag_gb: ABUSE UPDATE STARTING :flag_gb::flag_gb:\n"

    if n_abuse == 0:
        message += "Adam has, incredibly, remained totally unmolested today... I wonder how long that will last..."
    else:
        if n_abuse == 1:
            message += "Adam has *only* been abused once within the past 24 hours"
            if n_72 == 1:
                message += " and, of course, 72 did this single abuse."
            else:
                message += " but the abuser was not 72 this time!!"
        else:
            message += "Adam has been abused {} times in the past 24 hours".format(n_abuse)
            if n_72 == 1:
                message += " and 72 did only one of those abuses. There are some other badmins around..."
            elif n_72 == n_abuse:
                message += " and, of course, 72 is accountable for all of those abuses."
            else:
                message += " but 72 only accounts for {} of those abuses. Who are the other badmins?".format(n_72)

    message += "\n:flag_gb::flag_gb: ABUSE UPDATE FINISHED :flag_gb::flag_gb:"

    await channel.send(message)


@tasks.loop(hours=HOURS_IN_WEEK)
async def weekend_announcement():
    """Send a video of Daniel Craig saying it's the weekend."""

    guild = bot.get_guild(ID_SERVER)
    channel = guild.get_channel(ID_MAIN_CHANNEL)

    await channel.send(":clock6:", file=discord.File("videos/weekend.mp4"))


@weekend_announcement.before_loop
async def sleep_until_friday_night():
    """Determine how long it is until 6pm on Friday and sleep the bot until
    then."""

    now = datetime.datetime.now()
    next_friday_date = now + datetime.timedelta((c.FRIDAY - now.weekday()) % 7)
    when = datetime.datetime(
        year=next_friday_date.year, month=next_friday_date.month, day=next_friday_date.day, hour=18, minute=0, second=1
    )
    dt_till_friday_night = when - now
    sleep_time_seconds = dt_till_friday_night.days * 24 * 3600 + dt_till_friday_night.seconds
    utility.log("all", "waiting {:.1f} hours till posting weekend message".format(sleep_time_seconds / 3600))
    await asyncio.sleep(sleep_time_seconds)

    await bot.wait_until_ready()


@daily_message.before_loop
async def sleep_until_midnight():
    """Determine how long it is until the end of the day , then sleep the bot
    until that time + 5 seconds."""

    today = datetime.datetime.now()
    dt_till_midnight = datetime.datetime.combine((today + datetime.timedelta(days=1)), datetime.time.min) - today
    utility.log("all", "waiting {:.1f} hours till midnight".format(dt_till_midnight.seconds / 3600))
    await asyncio.sleep(dt_till_midnight.seconds + 5)

    await bot.wait_until_ready()


# Events -----------------------------------------------------------------------


@bot.event
async def on_command_error(ctx, error):
    """Send messages to the channel on certain errors."""

    if isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.send("Stop abusing me {0.name}, I'm a virgin!!".format(ctx.author))
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("That is an unknown command, you absolute fopdoodle.")
    else:
        utility.logerror("", error)


@bot.event
async def on_ready():
    """Prepare the bot at launch. This opens the logfile, prints the guilds the
    bot is currently in and registers the atexit function."""

    welcomemsg = "Logged in as {0.user} in the current guilds:".format(bot)
    for n, guild in enumerate(bot.guilds):
        welcomemsg += "\n\t{0}). {1.name} ({1.id})".format(n, guild)
    utility.log("all", welcomemsg)


# Misc functions ---------------------------------------------------------------


def atclose():
    """At exit, we want to close the logfile and teach the bot any new phrases
    which haven't been learned yet."""

    utility.close_logfile()


# Run --------------------------------------------------------------------------


daily_message.start()
weekend_announcement.start()
atexit.register(atclose)
bot.run(os.environ["BOT_TOKEN"])
