#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import time
import datetime
import numpy as np
import discord
from discord.ext import commands
from globals import *
from cogs import utility


class AdminAbuse(commands.Cog, name="Admin Abuse"):
    """Commands to combat admin abuse and to shame admin abusers."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Show how many admin abuses have been committed against Adam")
    @commands.cooldown(TIMES_B4_COOLDOWN, COOLDOWN_TIME_STANDARD, commands.BucketType.user)
    async def abuse(self, ctx, days=None):
        """Check the audit logs for abuses against the user within the last x hours
        and send a message to the server saying how many times they have been
        abused.
        Parameters
        ----------
        days: str
            The number of days of audit log history to search. Can be a
            fractional day, such as 0.5 for 12 hours."""

        if days is None:
            days = 1
        else:
            days = abs(float(days))

        hours = int(days * 24)

        now = datetime.datetime.today()
        after = now - datetime.timedelta(hours=hours)

        n_audit = n_abuses = 0
        async for abuse in ctx.guild.audit_logs(limit=MAX_AUDIT_QUERY, oldest_first=False):
            n_audit += 1

            # Break if we've gone far back in time, the filtering ability on
            # audit_logs didn't seem to work...

            if abuse.created_at < after:
                break

            # Ignore unbans, as these are not abuses

            if abuse.action == discord.AuditLogAction.unban:
                continue

            # Track the number of abuses, ignoring things done by the bot

            if abuse.target.id == ID_ABUSED and abuse.user.id != self.bot.user.id:
                n_abuses += 1

        if n_abuses == 0:
            await ctx.send("Adam has remained miraculously unmolested for the last {} hours... odd.".format(hours))
        elif n_abuses == 1:
            await ctx.send("Adam has been abused a single time in the past {} hours.".format(hours))
        else:
            message = "Adam has been abused a total of {} times".format(n_abuses)
            if n_audit == MAX_AUDIT_QUERY - 1:
                dt = abuse.created_at - now
                await ctx.send(
                    message + " in the last {:.0f} hours before I gave up looking.".format(round(dt.seconds / 3600))
                )
            else:
                await ctx.send(message + " in the last {:.0f} hours.".format(hours))

    @commands.command(description="Invite Adam back to the server")
    @commands.cooldown(TIMES_B4_COOLDOWN, COOLDOWN_TIME_STANDARD, commands.BucketType.user)
    async def invite(self, ctx):
        """Invite the user to the server via DM. This can be called in another
        server and still invite the user to #idiots. There is a 5 second cool down
        before the invite is sent."""

        if ID_ABUSED in utility.get_all_member_ids(self.bot.get_guild(ID_SERVER)):
            utility.logerror("all", "the user ({0}) is already in the server, not sending invite.".format(ID_ABUSED))
            return

        await self.send_invite()

    @commands.command(description="Show the previous crime committed against Adam")
    @commands.cooldown(TIMES_B4_COOLDOWN, COOLDOWN_TIME_STANDARD, commands.BucketType.user)
    async def last(self, ctx, limit=None):
        """Check the audit log for the last incident including the user as the
        target.
        Parameters
        ----------
        limit: int
            The number of audit logs to check."""

        if limit is None:
            limit = MAX_AUDIT_QUERY
        else:
            limit = abs(int(limit))
            if limit > MAX_AUDIT_QUERY:
                limit = MAX_AUDIT_QUERY

        n = 0
        user_abuse = None
        async for abuse in ctx.guild.audit_logs(limit=limit):
            n += 1
            if abuse.action == discord.AuditLogAction.unban:
                continue
            if abuse._target_id == ID_ABUSED and abuse.user.id != self.bot.user.id:
                user_abuse = abuse
                break

        # Rare cases when he has not been abused.

        if user_abuse is None or n == limit - 1:
            await ctx.send(
                "Adam has, surprisingly, not been abused in the last {} abuses recorded. Something is awry."
                .format(limit)
            )

        # Check the abusing action and create a message depending on the type of
        # abuse received and the reason why he was abused

        await ctx.send(utility.create_abuse_message(user_abuse))

    @commands.command(description="Print the mission statement", aliases=["purpose"],)
    @commands.cooldown(TIMES_B4_COOLDOWN, COOLDOWN_TIME_STANDARD, commands.BucketType.user)
    async def mission(self, ctx):
        """Send a message to the channel to say what the point of this bot is."""

        await ctx.send(
            "Hello, I am a bot here to protect Adam and his discord rights! I also tend to be abused by Zadeth."
        )

    @commands.command(description="Update Adam's roles")
    @commands.cooldown(TIMES_B4_COOLDOWN, COOLDOWN_TIME_STANDARD, commands.BucketType.user)
    async def roles(self, ctx):
        """Update the roles so the user is a Cunt and a Cunts and/or Lads."""

        if ctx.guild.id != ID_SERVER:
            await ctx.send("{0.author.name} pal, you're not in the correct server to request this.".format(ctx))
            return

        member = await ctx.guild.fetch_member(ID_ABUSED)
        await self.give_roles(member)

    @commands.cooldown(TIMES_B4_COOLDOWN, COOLDOWN_TIME_STANDARD, commands.BucketType.user)
    @commands.command(description="Unban Adam from the server and re-invite him")
    async def unban(self, ctx):
        """Unban the user from the server and re-invite."""

        guild = self.bot.get_guild(ID_SERVER)

        if ID_ABUSED in utility.get_all_member_ids(guild):
            utility.logerror("all", "unban: user already in server")
            return

        # Try to unban the user. Have to use self.bot.fetch_user because it's (very)
        # likely that the user is no longer in the guild if they have been banned.

        try:
            await ctx.guild.unban(await self.bot.fetch_user(ID_ABUSED))
        except discord.errors.NotFound as e:
            utility.logerror("all", str(e))

        await self.invite(ctx)

    async def send_invite(self):
        """Send an invite to the user for the #idiots text channel in Top Gays."""

        user = self.bot.get_user(ID_ABUSED)
        channel = self.bot.get_channel(ID_MAIN_CHANNEL)

        members = utility.get_all_member_ids(channel.guild)
        if ID_ABUSED in members:
            utility.logerror(channel.guild.name, "somehow {0.name} has rejoined before an invite needed to be sent???".format(user))
            return

        invite = await channel.create_invite(max_age=None, max_uses=1)
        await user.send(invite)
        utility.log(channel.guild.name, "invite sent to {0.name} ({0.id}) {1}".format(user, invite))

    async def give_roles(self, member):
        """Give a member the Cunts and the Lads and/or Cunts roles.
        Parameters
        ----------
        member: discord.Member
            The member to update."""

        try:
            roles = [
                discord.utils.get(member.guild.roles, id=ID_ROLE_SUB),
                discord.utils.get(member.guild.roles, id=ID_ROLE_MAIN)
            ]
        except Exception as e:
            utility.logerror(member.guild.name, "Couldn't fetch a role -- " + str(e))
            return

        for role in roles:
            try:
                await member.add_roles(role)
                utility.log(member.guild.name, "gave {0.name} the role {1.name} on join".format(member, role))
            except Exception as e:
                utility.logerror(member.guild.name, "Couldn't give {0.name} role -- ".format(member, role) + str(e))
                return

    @commands.Cog.listener("on_message_delete")
    async def respond_to_deleted_message(self, message):
        """Send the message or a silly message when Adam's message is deleted.
        todo: ignore message deletes by bots"""

        if message.author.id != ID_ABUSED:
            return

        xi = np.random.rand()

        if xi < 0.25:
            await message.channel.send("Here you go Adam pal, I intercepted this message from ya: " + message.content)
        elif xi < 0.5:
            await message.channel.send("Someone was made upset by Adam's message :joy:")

        utility.log(message.guild.name, "deleted message -- " + message.content)

    @commands.Cog.listener("on_member_join")
    async def give_roles_on_join(self, member):
        """Give the user a role on joining."""

        if member.id != ID_ABUSED or member.guild.id != ID_SERVER:
            return

        await give_roles(member)

    @commands.Cog.listener("on_member_remove")
    async def member_remove(self, member):
        """Invite the user back when kicked or banned, but first send the reason
        they were removed to the channel. There is a brief delay before an unban."""

        if member.id != ID_ABUSED:
            return

        guild = member.guild
        channel = guild.get_channel(ID_MAIN_CHANNEL)

        # Find the reason they left and construct a message to send. Only search
        # through the last 25 audit logs

        the_abuse = None
        async for abuse in guild.audit_logs(limit=25):
            if abuse._target_id == ID_ABUSED:
                the_abuse = abuse
                break

        # If we did find the reason for leaving, then just invite because something
        # has gone wrong

        if the_abuse is None:
            await self.send_invite()
            return

        # Construct a message as to why the user left

        how, reason = utility.get_remove_reason(the_abuse)

        if how == "left":
            await channel.send(":sob: Adam has left. RIP in peaces :sob:")
            await self.send_invite()
        else:
            if how == "banned":
                time.sleep(5)
                await member.unban()
            message = ":warning: {0.user.name} has {1} Adam {2} :warning:".format(the_abuse, how, reason)
            await channel.send(message)
