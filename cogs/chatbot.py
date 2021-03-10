#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
from discord.ext import commands
from discord.ext import tasks
from cogs import utility
from globals import *
from markovify import markovify
import shutil


BAD_WORD = os.environ["BAD_WORD"].lower()
BAD_WORD_PLURAL = BAD_WORD + "s"
BOT_RESPOND_CHANCE = 0.02


class SpamBot(commands.Cog, name="Spambot"):
    """Send helpful and very good messages to the chat."""

    def __init__(self, bot, tries=150):
        """Initialize the spam commands.
        Parameters
        ----------
        bot: discord.ext.commands.bot
            The Discord bot object.
        tries: int
            The maximum number of attempts to attempt to generate sentences."""

        self.bot = bot
        self.tries = tries
        self.messages = []

        # Initialize the Markov bot

        with open("trained/markov_chat.json", "r") as f:
            self.mc = markovify.Text.from_json(f.readlines()[0])

        # Now read in the other two word files to generate bad words and
        # god messages

        try:
            with open("words/badwords.txt", "r") as f:
                self.badwords = f.readlines()[0].split()
        except OSError:
            self.badwords = ["fuck", "nazi", "penis", "clit", "vagina"]

        try:
            with open("words/godwords.txt", "r") as f:
                self.godwords = f.readlines()
        except OSError:
            self.godwords = ["the", "cia", "fbi" "have", "gotten", "killed", "me", "compiler"]

        self.update_mc_bot_schedule.start()

    @commands.cooldown(TIMES_B4_COOLDOWN, COOLDOWN_TIME_STANDARD, commands.BucketType.user)
    @commands.command(description="Get the bot to say a naughty word")
    async def badword(self, ctx):
        """Speak a bad word into the chat. If a certain bad word is said, then
        a certain person gets tagged with the bad word."""

        badword = utility.get_badword(self.badwords)

        if badword == BAD_WORD or badword == BAD_WORD_PLURAL:
            member = ctx.message.guild.get_member(ID_USER_WORD)
            await ctx.send("Here's one for ya, {} pal... {}.".format(member.mention, badword.upper()))
        else:
            await ctx.send("{}.".format(badword.capitalize()))

    @commands.command(description="Make the bot speak some nonsense", aliases=["speak"])
    async def chat(self, ctx, *, words=None):
        """Generates a random sentence using the Markov Chain chat bot trained
        on this server. Will try to avoid creating messages which mention users,
        especially @here or @everyone. Can be used in DMs and other severs, but
        in TG this command will only work in #spam. There is no cooldown on this
        command because it only works in the spam channel.
        Parameters
        ----------
        words: str
            A word or set of words to start sentence generation with."""

        if ctx.guild:
            if ctx.guild.id == ID_SERVER and ctx.channel.id != ID_SPAM_CHANEL:
                await ctx.send("Use this command in #spam plz :angel:")
                return

        if ctx.guild == ID_SERVER:
            channel = self.bot.get_channel(ID_SPAM_CHANEL)
        else:
            channel = ctx.channel

        # When given a work, at first it will attempt to generate a sentence with
        # that word

        await channel.send(self.generate_mc_message(words, False))

    @commands.cooldown(TIMES_B4_COOLDOWN, COOLDOWN_TIME_STANDARD, commands.BucketType.user)
    @commands.command(description="Receive a message from god", aliases=["godword", "god"])
    async def oracle(self, ctx, n_words=None):
        """Send a message from the temple from God (Terry Davis/the Oracle).
        Parameters
        ----------
        n_words: str
            The number of words to generate for the sentence."""

        if n_words is None:
            n_words = np.random.randint(1, 15)
        else:
            try:
                n_words = int(n_words)
            except ValueError:
                await ctx.send("The oracle doesn't know of the number \"{}\"".format(n_words))

        await ctx.send(utility.get_god_message(n_words, self.godwords))

    @commands.cooldown(1, COOLDOWN_TIME_10_MIN, commands.BucketType.guild)
    @commands.command(description="Teach the bot some new phrases", aliases=["teach"])
    async def learn(self, ctx):
        """Force the MC bot to update its Markov Chain to learn new phrases."""

        if len(self.messages) == 0:
            if ctx:
                await ctx.send("I have nothing new to learn :disappointed:")
            return

        phrases = self.prepare_phrases()
        del self.messages[:]

        # Create a backup of the model,

        shutil.copy2("trained/markov_chat.json", "trained/markov_chat.json.bak")

        # Now teach a new model the new phrases and combine the chains together

        new_model = markovify.NewlineText(phrases)
        combined_chain = markovify.combine([self.mc.chain, new_model.chain])
        self.mc.chain = combined_chain
        with open("trained/markov_chat.json", "w") as f:
            f.write(self.mc.to_json())

        if ctx:
            await ctx.send("I have been taught {} new phrases :nerd:".format(len(phrases)))
        else:
            utility.log(ctx.guild.name, "Bot has learned {} new phrases".format(len(phrases)))

    def generate_mc_message(self, words=None, mentions=True):
        """Generate a message from the Markov Chain bot
        Parameters
        ----------
        words: str
            A seed word or seed words used for inspiration.
        mentions: bool
            Disable the ability to generate a message with
        Returns
        -------
        sentence: str
            The generated sentence."""

        sentence = None

        for _ in range(self.tries):
            if words:
                if len(words.split()) > 1:
                    try:
                        sentence = self.mc.make_sentence_with_start(words, tries=150, strict=False)
                    except (KeyError, markovify.text.ParamError):
                        sentence = self.mc.make_sentence()
                else:
                    try:
                        sentence = self.mc.make_sentence_that_contains(words)
                    except (KeyError, markovify.text.ParamError):
                        sentence = self.mc.make_sentence()
            else:
                sentence = self.mc.make_sentence()

            # Avoid generating messages which have mentions in them, but user
            # mentions are OK if specified

            if "@here" not in sentence and "@everyone" not in sentence:
                if mentions is False or (mentions is True and "<@" not in sentence):
                    break

        if sentence:
            return sentence.strip()

        mesg1 = self.godwords[np.random.randint(0, 4)]
        mesg2 = self.godwords[np.random.randint(0, 4)]

        return mesg1 + " my brain no worky " + mesg2

    def prepare_phrases(self):
        """Clean up the recorded lines/phrases which are to be taught to the MC
        bot. The aim is to exclude certain patterns and commands.
        Returns
        -------
        final: list
            A list of phrases to learn."""

        final = []

        for phrase in self.messages:

            # Ignore messages which start with certain characters

            if phrase.startswith("!"):
                continue
            if phrase.startswith("%"):
                continue
            if phrase.startswith("+"):
                continue
            if phrase.startswith("?"):
                continue

            # Ignore messages which have certain substrings in them

            if "@everyone" in phrase:
                continue
            if "@here" in phrase:
                continue

            final.append(phrase)

        return final

    @commands.Cog.listener("on_message")
    async def mc_respond(self, message):
        """Feed each message into the server into the chatbot and then processes
        the usual commands."""

        if message is None or message.content is None or len(message.content) == 0:
            return
        if message.author.id == self.bot.user.id:
            return

        self.messages.append(message.content)

        # todo: put into a function

        msg = message.content
        if msg[0] == "?" and msg[1] != "?" and len(msg) != 1:
            word = message.content.split()[0]
            await message.channel.send(self.generate_mc_message(word[1:], mentions=False))
        elif "nvda" in msg:
            bot_msg = self.generate_mc_message("nvda", mentions=False)
            if "nvda" in bot_msg:
                await message.channel.send(bot_msg)
            else:
                await message.channel.send("nvda big stonks :chart_with_downwards_trend:")
        else:
            if np.random.rand() < BOT_RESPOND_CHANCE:
                words = msg.split()
                await message.channel.send(
                    self.generate_mc_message(
                        words[np.random.randint(0, len(words))], mentions=True
                    )
                )

    @tasks.loop(hours=1)
    async def update_mc_bot_schedule(self):
        """Get the bot to update the chain every hour."""

        await self.learn(None)
