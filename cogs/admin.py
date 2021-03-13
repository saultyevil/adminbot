#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import time
import numpy as np
import discord
from discord.ext import commands
from globals import *
from cogs import utility


class AdminBot(commands.Cog, name="Moderation"):
    """Automatic moderation and commands when that fails."""

    def __init__(self, bot):
        """Initialize the admin commands and automatic moderation.
        Parameters
        ----------
        bot: discord.ext.commands.Bot
            The discord bot."""

        self.bot = bot

    # Commands -----------------------------------------------------------------

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

        if not ctx.guild:
            await ctx.send("This command only works in a server.")
            return

        if days is None:
            days = 1
        else:
            days = abs(float(days))

        hours = int(days * 24)

        n_abuses, n_72 = await utility.count_audit_log(self.bot.user.id, ctx.guild, hours)

        if n_abuses == 0:
            await ctx.send("Adam has remained miraculously unmolested for the last {} hours... odd.".format(hours))
        elif n_abuses == 1:
            await ctx.send("Adam has been abused a single time in the past {} hours.".format(hours))
        else:
            await ctx.send("Adam has been abused a total of {} times in the last {:.0f} hours.".format(n_abuses, hours))

    @commands.command(description="Invite Adam back to the server")
    @commands.cooldown(TIMES_B4_COOLDOWN, COOLDOWN_TIME_STANDARD, commands.BucketType.user)
    async def invite(self, ctx):
        """Invite the user to the server via DM. This can be called in another
        server and still invite the user to #idiots. There is a 5 second cool down
        before the invite is sent."""

        if ID_ABUSED in utility.get_all_user_ids(self.bot.get_guild(ID_SERVER)):
            utility.logerror("all", "the user ({0}) is already in the server, not sending invite.".format(ID_ABUSED))
            return

        await self.send_user_invite_to_server()

    @commands.command(description="Show the previous crime committed against Adam")
    @commands.cooldown(TIMES_B4_COOLDOWN, COOLDOWN_TIME_STANDARD, commands.BucketType.user)
    async def last(self, ctx, limit=None):
        """Check the audit log for the last incident including the user as the
        target.
        Parameters
        ----------
        limit: int
            The number of audit logs to check."""

        if not ctx.guild:
            await ctx.send("This command only works in a server.")
            return

        if limit is None:
            limit = MAX_AUDIT_QUERY
        else:
            limit = abs(int(limit))
            if limit > MAX_AUDIT_QUERY:
                limit = MAX_AUDIT_QUERY

        abuse = await utility.get_last_abuse(self.bot.user.id, ctx.guild, limit)

        # Rare cases when he has not been abused.

        if abuse is None:
            await ctx.send(
                "Adam has, surprisingly, not been abused in the last {} abuses recorded. Something is awry."
                .format(limit)
            )

        # Check the abusing action and create a message depending on the type of
        # abuse received and the reason why he was abused

        await ctx.send(utility.create_abuse_message(abuse))

    @commands.command(description="Print the mission statement", aliases=["purpose"])
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

        if not ctx.guild:
            await ctx.send("This command only works in a server.")
            return

        if ctx.guild.id != ID_SERVER:
            await ctx.send("{0.author.name} pal, you're not in the correct server to request this.".format(ctx))
            return

        member = await ctx.guild.fetch_member(ID_ABUSED)
        await self.give_user_roles(member)

    @commands.cooldown(TIMES_B4_COOLDOWN, COOLDOWN_TIME_STANDARD, commands.BucketType.user)
    @commands.command(description="Unban Adam from the server and re-invite him")
    async def unban(self, ctx):
        """Unban the user from the server and re-invite."""

        guild = self.bot.get_guild(ID_SERVER)
        user = await self.bot.fetch_user(ID_ABUSED)
        ban_list = await guild.bans()

        if ID_ABUSED in utility.get_all_user_ids(guild):
            utility.logerror("all", "unban: user already in server")
            return

        if ID_ABUSED not in utility.get_banned_user_ids(ban_list):
            utility.logerror("all", "unban: user is not in ban list")
            return

        # Try to unban the user. Have to use self.bot.fetch_user because it's (very)
        # likely that the user is no longer in the guild if they have been banned.
        # todo: check the server bans

        try:
            await guild.unban(user)
        except discord.errors.NotFound as e:
            utility.logerror("all", str(e))

        await self.invite(ctx)

    # Events -------------------------------------------------------------------

    @commands.Cog.listener("on_member_join")
    async def give_roles_on_join(self, member):
        """Give the user a role on joining."""

        if member.id != ID_ABUSED or member.guild.id != ID_SERVER:
            return

        await self.give_user_roles(member)

    @commands.Cog.listener("on_message")
    async def line_go_up_commands(self, message):
        """Tell the user who posted !wl in the wrong channel that it's the
        wrong channel."""

        if not message.guild:
            return

        if message.guild.id != ID_SERVER:
            return

        msg = message.content

        for cmd in ["!wl", "!quote", "!earnings", "!cryptos"]:
            if msg.startswith(cmd) and message.channel.id != ID_WL_CHANNEL:
                wl_channel = message.guild.get_channel(ID_WL_CHANNEL)
                await message.channel.send(
                    ":rotating_light: {1.author.mention} that {0} command belongs in {2.mention} :rotating_light:"
                    .format(cmd, message, wl_channel), delete_after=30
                )
                return

    @commands.Cog.listener("on_message_delete")
    async def respond_to_deleted_message(self, message):
        """Send the message or a silly message when Adam's message is deleted."""

        if message.author.id != ID_ABUSED:
            return
        if not message.guild:
            return

        guild = message.guild
        found_in_audit = False
        async for entry in guild.audit_logs(limit=50, action=discord.AuditLogAction.message_delete):
            if entry.target:
                if entry.target.id == message.id:
                    found_in_audit = True
                    if entry.user.id == ID_BOT_IGNORE or entry.user.id == ID_ABUSED:
                        return

                    break

        if not found_in_audit:
            return

        xi = np.random.rand()

        if xi < 0.05:
            await message.channel.send(
                "Here you go Adam pal, I intercepted this message from ya: " + message.content
            )
        elif xi < 0.1:
            await message.channel.send("Someone was made upset by Adam's message :joy:")

    @commands.Cog.listener("on_member_remove")
    async def send_member_remove_message(self, member):
        """Invite the user back when kicked or banned, but first send the reason
        they were removed to the channel. There is a brief delay before an unban."""

        if member.id != ID_ABUSED:
            return

        guild = member.guild
        channel = guild.get_channel(ID_MAIN_CHANNEL)
        ban_list = await guild.bans()

        # Find the reason they left and construct a message to send. Only search
        # through the last 25 audit logs

        abuse = None
        async for entry in guild.audit_logs(limit=50):
            if entry.target:
                if entry.target.id == ID_ABUSED:
                    abuse = entry
                    break

        # If we did find the reason for leaving, then just invite because something
        # has gone wrong

        if not abuse:
            await self.send_user_invite_to_server()
            return

        # Construct a message as to why the user left

        how, reason = utility.get_remove_reason(abuse)

        if how == "unknown":
            await channel.send(":sob: Adam has gone :sob:")
            if ID_ABUSED in ban_list:
                await member.unban()
            await self.send_user_invite_to_server()
        else:
            if how == "banned":
                time.sleep(5)
                await member.unban()
            message = ":warning: {0.user.name} has {1} Adam {2} :warning:".format(abuse, how, reason)
            await channel.send(message)
            await self.send_user_invite_to_server()

    # Functions ----------------------------------------------------------------

    async def give_user_roles(self, member):
        """Give a member the Cunts and the Lads and/or Cunts roles.
        Parameters
        ----------
        member: discord.Member
            The member to update."""

        guild = self.bot.get_guild(ID_SERVER)

        try:
            roles = [
                guild.get_role(ID_ROLE_SUB), guild.get_role(ID_ROLE_MAIN)
            ]
        except Exception as e:
            utility.logerror(guild.name, "Couldn't fetch a role -- " + str(e))
            return

        for role in roles:
            try:
                await member.add_roles(role)
                utility.log(guild.name, "gave {0.name} the role {1.name} on join".format(member, role))
            except Exception as e:
                utility.logerror(guild.name, "Couldn't give {0.name} role -- ".format(member, role) + str(e))
                return

    async def send_user_invite_to_server(self):
        """Send an invite to the user for the #idiots text channel in Top Gays."""

        user = self.bot.get_user(ID_ABUSED)
        channel = self.bot.get_channel(ID_MAIN_CHANNEL)

        members = utility.get_all_user_ids(channel.guild)
        if ID_ABUSED in members:
            utility.logerror(
                channel.guild.name, "somehow {0.name} has rejoined before an invite needed to be sent???"
                .format(user)
            )
            return

        invite = await channel.create_invite(max_age=3600, max_uses=1)
        await user.send(invite)
        utility.log(channel.guild.name, "invite sent to {0.name} ({0.id}) {1}".format(user, invite))
