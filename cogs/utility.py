#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""General purpose utility functions for the bot. Mostly logging functions, but
I'm sure at some point the bot will become more modular."""


import pathlib
import discord
import datetime
import numpy as np

from globals import *


async def count_audit_log(bot_id, guild, hours=24, limit=MAX_AUDIT_QUERY):
    """Count the number of abuses in the audit log against Adam, and return
    abuse reason.
    Parameters
    ----------
    bot_id: int
        The ID number for the bot, we will ignore this.
    guild: discord.Guild
        The Guild object to search the audit logs for.
    hours: float
        The number of hours back to search in the audit logs.
    limit: int
        The number of audit logs to search through."""

    now = datetime.datetime.today()
    after = now - datetime.timedelta(hours=hours)

    n_audit = n_abuses = n_72 = 0
    async for entry in guild.audit_logs(limit=limit, oldest_first=False):
        n_audit += 1

        # Break if we've gone too far back in time, the filtering ability on
        # audit_logs didn't seem to work...

        if entry.created_at < after:
            break

        # Ignore unbans, as these are not abuses

        if entry.action == discord.AuditLogAction.unban:
            continue

        # Track the number of abuses, ignoring things done by the bot

        if entry.target:  # sometimes entry.target is None
            if entry.target.id == ID_ABUSED and entry.user.id != bot_id:
                n_abuses += 1
                if entry.user.id == ID_ABUSER:
                    n_72 += 1

        return n_abuses, n_72


def create_abuse_message(audit_entry):
    """Create a message explain how the user was abused.
    Parameters
    ----------
    audit_entry: discord.AuditLogEntry
        The audit log entry to construct the message for."""

    message = "The latest breach of Adam's human rights was caused by {0.user.name} ".format(audit_entry)
    if audit_entry.action == discord.AuditLogAction.ban:
        message += "banning "
        if audit_entry.reason is None:
            message += "for no reason."
        else:
            message += "because \"{}\".".format(audit_entry.reason.strip())
    elif audit_entry.action == discord.AuditLogAction.kick:
        message += "kicking "
        if audit_entry.reason is None:
            message += "for unknown reasons."
        else:
            message += "because \"{}\".".format(audit_entry.reason.strip())
    else:
        message += "with a " + audit_entry.action.name.replace("_", " ") + "."

    return message


def get_all_user_ids(guild):
    """Get all the members in a guild.
    Parameters
    ----------
    guild: discord.Guild
        The guild to find the member ids for."""

    return [member.id for member in guild.members]


def get_badword(badwords=None):
    """Pick a random badword from the provided bad words, or from some
    pre-defined badwords.
    Parameters
    ----------
    badwords: list [optional]
        A list of bad words."""

    if badwords is None:
        badwords = [
            "nazi", "hitler", "fuck", "communist", "penis", "vagina", "dick",
            "cunt", "boris", "johnson", "brexit", "loser", "npc", "bot"
        ]

    return badwords[np.random.randint(0, len(badwords))]


def get_banned_user_ids(ban_list):
    """Get the user IDs for the banned members in a guild.
    Parameters
    ----------
    ban_list: discord.BanEntry
        A list of ban entries."""

    return [ban.user.id for ban in ban_list]


def get_god_message(n_words, godwords=None):
    """Get a God message, which is a sentence of random length of random words.
    Parameters
    ----------
    n_words: int
        The number of words in the sentence.
    godwords: list
        A list of god words."""

    if godwords is None:
        return "The Oracle is sleeping, please leave them alone."

    if n_words < 1:
        n_words = np.random.randint(1, 15)

    vocab_len = len(godwords)
    godwords = [word.replace("\n", "") for word in godwords]

    message = "{}".format(godwords[np.random.randint(0, vocab_len)])
    for _ in range(1, n_words):
        message += " {}".format(godwords[np.random.randint(0, vocab_len)])

    return message


async def get_last_abuse(bot_id, guild, limit=MAX_AUDIT_QUERY):
    """Get the last abuse of Adam in the audit log.
    Parameters
    ----------
    bot_id: int
        The ID number for the bot, we will ignore this.
    guild: discord.Guild
        The Guild object to search the audit logs for.
    limit: int
        The number of audit logs to search through."""

    abuse = None
    async for entry in guild.audit_logs(limit=limit):
        if entry.action == discord.AuditLogAction.unban:
            continue
        if entry.target:
            if entry.target.id == ID_ABUSED and entry.user.id != bot_id:
                abuse = entry
                break

    return abuse


def get_remove_reason(audit_entry):
    """Create a message explaining why the user was removed.
    Parameters
    ----------
    audit_entry: discord.AuditLogEntry
        The audit log entry to construct the message for."""

    if audit_entry.action == discord.AuditLogAction.ban:
        how = "banned"
    elif audit_entry.action == discord.AuditLogAction.kick:
        how = "kicked"
    else:
        return "unknown", ""

    if audit_entry.reason is None:
        reason = "for no reason"
    else:
        reason = "because '{0}'".format(audit_entry.reason.strip())

    return how, reason


# Logging ----------------------------------------------------------------------


LOGFILE = None


def close_logfile():
    """Close the logfile, which is kept in the global variable LOGFILE."""

    global LOGFILE
    if LOGFILE:
        LOGFILE.close()


def open_logfile():
    """Open the logfile for appending messages. The logfile pointer is stored in
    a global variable, as can be seen by the keyword GLOBAL."""

    global LOGFILE
    try:
        pathlib.Path("log/").mkdir(parents=True, exist_ok=True)
        logname = "shitbot_log-{}.txt".format(datetime.datetime.now().strftime("%Y-%m-%d"))
        LOGFILE = open("log/" + logname, "a")
        print("opened logfile with name", logname)
    except OSError:
        print("unable to open log file")
        return


def log(guild_name, msg):
    """Send a message to the terminal.
    Parameters
    ----------
    guild_name: str
        The name for the guild being logged.
    msg: str
        The message to log."""

    msg = "{}:{}:log: {}".format(guild_name, datetime.datetime.today(), msg)
    if LOGFILE is not None:
        LOGFILE.write(msg + "\n")
        LOGFILE.flush()
    print(msg)


def logerror(guild_name, msg):
    """Send an error message to the terminal.
    Parameters
    ----------
    guild_name: str
        The ID for the guild being logged.
    msg: str
        The message to log."""

    msg = "{}:{}:error: {}".format(guild_name, datetime.datetime.today(), msg)
    if LOGFILE is not None:
        LOGFILE.write(msg + "\n")
        LOGFILE.flush()
    print(msg)
