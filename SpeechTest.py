"""
Updating my Markov Chain algorithm
"""
 
# Dependencies
from random import randint
from time import sleep
 
# Globals
BOT_NAME = "NewMarkov"
BOT_VERS = "1.0.0"
PREFIX = "#?"
 
"""
 
     Markov chain functions
 
"""
 
# Globals
LIBRARY = []
FIRST_WORDS = []
LOADED = False
 
def outp(message):
    print(message)
 
 
def add_to_library(sentence):
    """Add word pairings from a sentence to the library"""
 
    # Globals
    global LIBRARY
    global FIRST_WORDS
    global LOADED
 
    # Save the sentence as is for filtering tests later
    if LOADED == True:
        f = open("UnfilteredLines.txt","a")
        f.write(sentence+"\n")
        f.close()
 
    # Split the sentence into words
    sentence = sentence.split(" ")
    # if sentence is too short to process, exit
    if len(sentence) < 3:
        return
 
    # Remove/replace websites, user mentions, and custom Discord emojis
    for x in range(0,len(sentence)):
        if sentence[x][0:9] == "@everyone":
            sentence[x] = "everyone"
        if sentence[x][0:5] == "@here":
            sentence[x] = "here"
        if sentence[x][0:4] == "http" or sentence[x][0:5] == "<http":
            sentence[x] = "website"
        if sentence[x][0:2] == "<@":
            sentence[x] = "user"
        if sentence[x][0:2] == "<#":
            sentence[x] = "channel"
        if sentence[x][0:2] == "<:":
            sentence[x] = "emoji"
 
    # Append the first two words to the first word library
    FIRST_WORDS.append([sentence[0], sentence[1]])
 
    # Report to console
    if LOADED == True:
        outp("Adding to library: " + ' '.join(sentence))
 
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
    # Start with a random first word
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
    if is_duplicated(sentence) == True:
        print("This one is duplicated:")
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
         
    f = open("OutputBrain.txt","r")
    lines = f.readlines()
    for line in lines:
        add_to_library(line[0:len(line)-1])
    LOADED = True
 
def save_library():
    """Save library to file"""
    all_lines = []
    words = []
    for word_pair in LIBRARY:
        words.append(word_pair[0])
        if word_pair[1] == "\n":
            all_lines.append(' '.join(words))
            words = []
 
    f = open("OutputBrain.txt","w")
    for line in all_lines:
        f.write(line+"\n")
    f.close()
 
load_library()
while(1):
    print(construct_sentence())
    sleep(4)
