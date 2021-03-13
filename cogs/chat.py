#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import time
import numpy as np
from discord.ext import commands
from discord.ext import tasks
from cogs import utility
from globals import *
from markovify import markovify
import shutil


BAD_WORD = os.environ["BAD_WORD"].lower()
BAD_WORD_PLURAL = BAD_WORD + "s"
BOT_RESPOND_CHANCE = 0.01


class SpamBot(commands.Cog, name="Spam"):
    """Send helpful and very good messages to the chat."""

    def __init__(self, bot, tries=150):
        """Initialize the spam commands.
        Parameters
        ----------
        bot: discord.ext.commands.Bot
            The Discord bot object.
        tries: int
            The maximum number of attempts to attempt to generate sentences."""

        self.bot = bot
        self.tries = tries
        self.messages = []

        # Initialize the Markov bot

        start = time.time()
        with open("trained/markov_chat.json", "r") as f:
            self.mc = markovify.Text.from_json(f.readlines()[0])
        utility.log("all", "It took {:.2f} seconds to load the MC model".format(time.time() - start))

        # Now read in the other two word files to generate bad words and
        # god messages

        try:
            with open("cogs/words/badwords.txt", "r") as f:
                self.badwords = f.readlines()[0].split()
        except OSError:
            utility.logerror("all", "couldn't load badwords")
            self.badwords = ["fuck", "nazi", "penis", "clit", "vagina"]

        try:
            with open("cogs/words/godwords.txt", "r") as f:
                self.godwords = f.readlines()
        except OSError:
            utility.logerror("all", "couldn't load godwords")
            self.godwords = ["the", "cia", "fbi" "have", "gotten", "killed", "me", "compiler"]

        self.schedule_update_mc_chains.start()

    # Commands -----------------------------------------------------------------

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
            if ctx.guild.id == ID_SERVER and ctx.channel.id != ID_SPAM_CHANNEL:
                await ctx.send(
                    "{0.author.mention} pls use this command in {1.mention} :angel:"
                    .format(ctx, ctx.guild.get_channel(ID_SPAM_CHANNEL))
                )
                return

        await ctx.send(self.mc_generate_message(words, allow_mentions=False))

    @commands.cooldown(1, COOLDOWN_TIME_10_MIN, commands.BucketType.guild)
    @commands.command(description="Teach the bot some new phrases", aliases=["teach"])
    async def learn(self, ctx):
        """Force the MC bot to update its Markov Chain to learn new phrases."""

        if len(self.messages) == 0:
            if ctx:
                await ctx.send("I have nothing new to learn :disappointed:")
            else:
                utility.log("all", "nothing new to teach mc bot")
            return

        phrases = self.get_teachable_phrases()
        del self.messages[:]

        if len(phrases) == 0:
            if ctx:
                await ctx.send("I have nothing new and safe to learn :disappointed:")
            else:
                utility.log("all", "nothing new and safe to teach mc bot")
            return

        # Create a backup of the model,

        shutil.copy2("trained/markov_chat.json", "trained/markov_chat.json.bak")

        # Now teach a new model the new phrases and combine the chains together

        try:
            new_model = markovify.NewlineText(phrases)
        except KeyError:
            utility.logerror("all", "key error when mc bot learning new sentences")
            return

        combined_chain = markovify.combine([self.mc.chain, new_model.chain])
        self.mc.chain = combined_chain
        with open("trained/markov_chat.json", "w") as f:
            f.write(self.mc.to_json())

        if ctx:
            await ctx.send("I have been taught {} new phrases :nerd:".format(len(phrases)))
        else:
            utility.log("all", "Bot has learned {} new phrases".format(len(phrases)))

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

    # Events -------------------------------------------------------------------

    @commands.Cog.listener("on_message")
    async def mc_respond_to_message(self, message):
        """Feed each message into the server into the chatbot and then processes
        the usual commands."""

        # if message is None:
        #     return
        # elif len(message.content) <= 1:
        #    return

        if message.author.id in [self.bot.user.id, ID_BOT_IGNORE]:
            return

        msg = message.content
        self.messages.append(msg)

        if msg.startswith("?") and len(msg) > 1:
            if msg[1] == "?":
                return
            word = message.content.split()[0]
            await message.channel.send(self.mc_generate_message(word[1:], allow_mentions=False))
        elif "nvda" in msg:
            bot_msg = self.mc_generate_message("nvda", allow_mentions=False)
            if "nvda" in bot_msg:
                await message.channel.send(bot_msg)
            else:
                await message.channel.send("nvda big stonks :chart_with_downwards_trend:")
        else:
            if np.random.rand() < BOT_RESPOND_CHANCE:
                if message.channel.id != ID_MAIN_CHANNEL:
                    return
                utility.log(message.guild.name, "the mc bot sent a message")
                words = msg.split()
                await message.channel.send(
                    self.mc_generate_message(
                        words[np.random.randint(0, len(words))], allow_mentions=True
                    )
                )

    # Scheduled tasks ----------------------------------------------------------

    @tasks.loop(hours=1)
    async def schedule_update_mc_chains(self):
        """Get the bot to update the chain every hour."""

        await self.learn(None)

    # Functions ----------------------------------------------------------------

    def mc_generate_message(self, words=None, allow_mentions=False):
        """Generate a message from the Markov Chain bot. By default messages with
        @everyone and @here in them will be discarded.
        Parameters
        ----------
        words: str
            A seed word or seed words used for inspiration.
        allow_mentions: bool
            Disable the ability to generate a message with a mention.
        Returns
        -------
        sentence: str
            The generated sentence."""

        sentence = None

        for _ in range(self.tries):
            if words:
                try:
                    if len(words.split()) > 1:
                        sentence = self.mc.make_sentence_with_start(words)
                    else:
                        sentence = self.mc.make_sentence_that_contains(words)
                except (IndexError, KeyError, markovify.text.ParamError):
                    sentence = self.mc.make_sentence()
            else:
                sentence = self.mc.make_sentence()

            # Avoid generating messages which have mentions in them, but user
            # mentions are OK if specified

            if "@here" not in sentence and "@everyone" not in sentence:
                if allow_mentions:
                    break
                else:
                    if "@" not in sentence:
                        break

        return sentence.strip()

    def get_teachable_phrases(self):
        """Clean up the recorded lines/phrases which are to be taught to the MC
        bot. The aim is to exclude certain patterns and commands.
        Returns
        -------
        learnable: list
            A list of phrases to learn."""

        learnable = []

        for phrase in self.messages:

            if len(phrase) == 0:
                continue

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

            if "@" in phrase:
                continue

            learnable.append(phrase)

        return learnable
