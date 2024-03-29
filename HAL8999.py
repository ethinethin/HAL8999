#
# HAL8999 - a ghetto Markov chain speech bot
# AUTHOR: EASTER
#
# HAL8999.py - the primary bot file
#
# Copyright (c) 2017 Easter <ethinethin@gmail.com>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# TO DO:
#
# Fix event stuff - use discord.ext.commands appropriately
# Add private commands
# Add stats commands
# Add timing for random (not triggered by in-channel text) sentences?
#

# Import Dependencies
import discord
from discord.ext import commands
import time
import asyncio
import sys
from random import randint

# Bot identification information
BOT_OWNER = "Ethinethin"
BOT_NAME = "HAL8999"
BOT_VERS = "6.0.0"
PREFIX = "#?"

# Values for sentence probability - on message, generate a random number between
# 1 and MAX. If that number is VALUE, construct a sentence.
MAX = 40
VALUE = 25

# terminal colors
class cols:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    DEFAULT = '\033[0m'

"""

     Bot operation functions

"""

def timestamp():
    """Return a formatted timestamp"""
    return(time.strftime("%Y-%b-%d %T"))

def outp(str):
    """Format and display message on console"""
    print("*** " + timestamp() + ": " + str)

def load_token():
    """Load the bot token from file"""
    outp("Loading bot token from Token.txt")
    try:
        f = open("Token.txt","r")
        lines = f.readlines()
        for line in lines:
            return line[0:len(line)-1]
    except:
        outp("No file Token.txt. Cannot connect to Discord.")
        sys.exit()

def startup():
    """Bot startup"""
    global bot
    outp(BOT_NAME + " v" + BOT_VERS + " loaded.")
    load_library()
    bot.run(load_token())



"""

     Markov chain functions

"""

# Globals
LIBRARY = []
FIRST_WORDS = []
LOADED = False

def add_to_library(sentence):
    """Add word pairings from a sentence to the library"""

    # Globals
    global LIBRARY
    global FIRST_WORDS
    global LOADED

    # Split the sentence into words
    sentence = sentence.split(" ")
    # if sentence is too short to process, exit
    if len(sentence) < 3:
        return

    for x in range(0,len(sentence)):

        # Remove/replace websites, user mentions, and custom Discord emojis
        if sentence[x][0:9] == "@everyone":
            sentence[x] = "everyone"
        if sentence[x][0:5] == "@here":
            sentence[x] = "here"
        if sentence[x][0:4] == "http" or sentence[x][0:5] == "<http":
            sentence[x] = ""
        if sentence[x][0:2] == "<@":
            sentence[x] = BOT_OWNER
        if sentence[x][0:2] == "<#":
            sentence[x] = ""
        if sentence[x][0:2] == "<:":
            sentence[x] = ""

        # Change mentions of the bot to "buddy" - this is the best solution I have
        # come up with for making sure the bot does not refer to himself
        if sentence[x].lower() == "hal":
            sentence[x] = BOT_OWNER
        if sentence[x].lower() == "hal?":
            sentence[x] = BOT_OWNER + "?"
        if sentence[x].lower() == "hal.":
            sentence[x] = BOT_OWNER + "."
        if sentence[x].lower() == "hal,":
            sentence[x] = BOT_OWNER + ","
        if sentence[x].lower() == "hal!":
            sentence[x] = BOT_OWNER + "!"
        if sentence[x].lower() == "hal's":
            sentence[x] = BOT_OWNER + "'s"

    # Append the first two words to the first word library
    FIRST_WORDS.append([sentence[0], sentence[1]])

    # Report to console
    if LOADED == True:
        outp(cols.BLUE + "Adding to library: " + cols.DEFAULT + ' '.join(sentence))

    # Add every word pairing to the library
    for x in range(0, len(sentence)):
        if x < len(sentence) - 2:
            LIBRARY.append([sentence[x], sentence[x+1], sentence[x+2]])
        else:
            LIBRARY.append([sentence[x], sentence[x+1], "\n"])
            return

def is_duplicated(sentence):
    """Check if sentence is duplicated in the library"""

    f = open("OutputBrain.txt", "r")
    lines = f.readlines()
    for line in lines:
        if line.lower() == sentence.lower() + "\n":
            return True
    f.close()
    return False

def construct_sentence():
    """Construct a sentence based on the library pairings"""
    # Start with a random first word pair
    sentence = FIRST_WORDS[randint(0,len(FIRST_WORDS)-1)]

    # Build a sentence
    while(1):
        # Current word is the last word of the sentence
        cur_pair = [sentence[len(sentence)-2], sentence[len(sentence)-1]]
        # If the last word is \n, that's the end of the sentence
        if(cur_pair[1] == "\n"):
            sentence = sentence[0:len(sentence)-1]
            break
        # Other wise, keep building the sentence
        else:
            # Find every triplet where the first two words are in the current pair
            triplets = []
            for word_triplet in LIBRARY:
                if word_triplet[0].lower() == cur_pair[0].lower() and word_triplet[1].lower() == cur_pair[1].lower():
                    triplets.append(word_triplet)
            # Append a random word from these pairings
            sentence.append(triplets[randint(0,len(triplets)-1)][2])

    # Join the words into a sentence
    sentence = ' '.join(sentence)
    # If the sentence is too short, try again
    if(len(sentence.split(" ")) < 5):
        sentence = construct_sentence()
    # If the sentence is duplicated, try to generate a new one, unless there are
    # fewer than 100 sentences of training data
    if is_duplicated(sentence) == True:
        try:
            sentence = construct_sentence()
        except:
            outp("Attempted to construct a unique sentence but could not.")
            return("")
    return(sentence)

def load_library():
    """Load library from file"""
    global LOADED
    outp("Loading brain from OutputBrain.txt")
    try:
        f = open("OutputBrain.txt", "r")
    except IOError:
        outp("Could not read file, starting fresh")
        LOADED = True
        return

    lines = f.readlines()
    for line in lines:
        add_to_library(line[0:len(line)-1])
    LOADED = True
    f.close()

def save_library():
    """Save library to file"""
    all_lines = []
    words = []
    for word_pair in LIBRARY:
        words.append(word_pair[0])
        if word_pair[2] == "\n":
            words.append(word_pair[1])
            all_lines.append(' '.join(words))
            words = []

    f = open("OutputBrain.txt","w")
    for line in all_lines:
        f.write(line+"\n")
    f.close()


"""

     Bot operation commands

"""
bot = commands.Bot(command_prefix=PREFIX)

@bot.event
async def on_ready():
    """Bot connected and ready"""
    outp("Logged in as: [{}]".format(bot.user))
    servers = []
    for guild in bot.guilds:
        servers.append(guild.name)
    outp("Connected to " + str(len(servers)) + " servers:")
    for server in servers:
        outp("\t" + server)

@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.abc.PrivateChannel):
        # Log and ignore private messages
        outp(cols.RED + "Private message from " + str(message.author) + ": " + cols.DEFAULT + message.content)
        f = open("PrivateMessages.txt","a")
        f.write(timestamp() + " " + str(message.author) + ": " + message.content + "\n")
        f.close()
    elif str(message.channel) == "general":
        # Only listen to non-bot, non-empty messages in #general channels
        if message.author.bot == False and message.content != "":
            # Split messages by newlines - needed for multi-line messages
            all_lines = message.content.split("\n")
            for line in all_lines:
                add_to_library(line)
            # Save library to file
            save_library()
            # Send a message to #general at random based on user specified global values
            if randint(0,MAX) == VALUE:
                sentence = construct_sentence()
                if sentence != "":
                    await asyncio.sleep(4)
                    try:
                        await message.channel.send(sentence)
                        outp(cols.GREEN + "Sending to channel: " + cols.DEFAULT + sentence)
                    except:
                        outp("Error raised while trying to send sentence")
                        pass

try:
    startup()
except:
    outp("Error received: "+str(sys.exc_info()[0]))
    sys.exit()
