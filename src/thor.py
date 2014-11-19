#!/usr/bin/python


'''
THOR connects to an IRC network, joins a channel, and keeps a log of everything that goes on.
WolframAlpha integration will come later.
'''

# TWISTED Imports
from twisted.words.protocols import irc

# INTERNAL Imports

#SYS Imports
import random
import shelve
import datetime
import time

#OTHER Imports
import ConfigParser
import feedparser
import ctypes
from operator import itemgetter

#HTTP Handlers
import requests

#Version Information

#None of the following lines down to the config parser are of any consequence
#to the code itself, and were merely added to poke fun at the sometimes
#arbitrary nature of version numbers in software today.
from src.modules import goslate

versionName = "Magni"
versionNumber = "19-11-2014 GMT+1-1541 | MAGNI"
versionEnv = "Python 2.7.3"

ctypes.windll.kernel32.SetConsoleTitleA("THORBot @ Valhalla")

#Config parser. Could be replaced in the future?

cfg = ConfigParser.RawConfigParser(allow_no_value=True)
cfg.read("magni.ini")


class ThorBot(irc.IRCClient):
    """
    Primary IRC class. Controls just about everything that isn't a module.
    Below you'll find a bunch of options that are handled by hammer.ini.
    """

    def __init__(self):
        #TODO Cthulhu must answer for his crimes against my code!
        #nickname = cfg.get('Bot Settings', 'Nickname')
        #password = cfg.get('Bot Settings', 'NickPass')
        #realname = "THORBot @ VALHALLA"
        nickname = 'Magni'
        password = ''
        realname = 'Magni[THORBOT] @ VALHALLA'

        self.realname = realname
        self.nickname = nickname
        self.password = password
        self.lineRate = 1

    def connectionMade(self):
        #First we connect
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def irc_ERR_ERRONEUSNICKNAME(self, prefix, params):
        print "irc_ERR_ERRONEUSNICKNAME called"

    def irc_ERR_PASSWDMISMATCH(self, prefix, params):
        print "!!!INCORRECT PASSWORD!!!\n Check hammer.ini for the NICKPASS parameter"
        return

    #TODO Rectify the lack of irc_RPC responses. It's an outrage.

    #EVENTS

    def signedOn(self):
        #Called when signing on
        print "Signed on successfully"
        self.join(self.factory.channel)

    def joined(self, channel):

        #Called when joining a channel
        print "Joined %s" % channel
        self.sendLine("MODE {nickname} {mode}".format(nickname=self.nickname, mode="+B"))

    def userJoined(self, user, channel):

        #Checks when a user joins if there are any reminders available for them
        sh = shelve.open('reminders')
        rfor = user
        reminder = sh[rfor]
        if KeyError:
            pass
        reply = "[%s] %s" % (user, reminder)
        self.msg(channel, reply)

        #And deletes them
        del sh[rfor]

        #Called when another user joins a channel
        print "%s has joined %s" % (user, channel)

    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]

        if msg:
            sh = shelve.open('reminders')
            rfor = user
            check = sh.has_key(rfor)

            if check is True:
                #Checks if key exists
                reminder = sh[rfor]
                reply = "[%s] %s" % (user, reminder)
                self.msg(channel, reply)

                #And deletes them
                del sh[rfor]

            elif check is False:
                pass

        #Calculator

        #TODO Add a !calc command that works. Is that too much to ask? (SPOILER: Yes. Yes it is.)

        if msg.startswith("!calc" or "!Calc"):

            if IndexError:
                error = "ERROR: list index out of range"
                self.msg(channel, error)
                return

            calclist = msg.split(' ')

            #Fetch arguments

            calc1 = itemgetter(1)(calclist)
            opera = itemgetter(2)(calclist)
            calc2 = itemgetter(3)(calclist)

            #Translate to int
            calc1 = int(calc1)
            calc2 = int(calc2)

            #Check if Operator is valid
            valid = ['+', '/', '-', '*']

            if calc1 == int(calc1):
                pass
            if calc1 != int(calc1):
                msg = "ERROR: ARG1 INCORRECT"
                self.msg(channel, msg)

            if opera in valid:
                pass
            if opera not in valid:
                msg = "ERROR: OPERATOR INCORRECT"
                self.msg(channel, msg)

            if calc2 == int(calc2):
                pass
            if calc2 != int(calc2):
                msg = "ERROR: ARG2 INCORRECT"
                self.msg(channel, msg)

            if opera is '+':
                result = calc1 + calc2
                reply = "%s + %s = %s" % (calc1, calc2, result)
                self.msg(channel, reply)

            if opera is '/':
                result = calc1 / calc2
                reply = "%s / %s = %s" % (calc1, calc2, result)
                self.msg(channel, reply)

            if opera is '-':
                result = calc1 - calc2
                reply = "%s - %s = %s" % (calc1, calc2, result)
                self.msg(channel, reply)

            if opera is '*':
                result = calc1 * calc2
                reply = "%s * %s = %s" % (calc1, calc2, result)
                self.msg(channel, reply)

        #Dice Roll

        if msg == "!roll":
            dice = random.randint(1, 100)
            dice = str(dice)

            self.msg(channel, dice)

        #Help utilities

        if msg.startswith("!help bbc"):
            msg = "Retrieves the most recent news article from BBC News and posts a summary. Use !bbc random for a" \
                  "random, recent news story. "
            self.msg(channel, msg)

        if msg.startswith("!help roll"):
            msg = "'Rolls' a number between 1 and 100."
            self.msg(channel, msg)

        if msg.startswith("!help me"):
            msg = "I'm sorry, I can't help you."
            self.msg(channel, msg)

        if msg.startswith("!help t"):
            msg = "Takes two arguments; A and B. Argument A will be the source language, argument B will be the target" \
                  " language. Languages follow ISO 639-1. (See: http://goo.gl/nVuDQJ )"
            self.msg(channel, msg)

        if msg.startswith("!help dt"):
            msg = "Detects the language the sentence is written in and returns a translation in English. No language" \
                  " codes are required."
            self.msg(channel, msg)

        if msg.startswith("!help qdb"):
            msg = "Fetches the quote with the number requested. Lazily coded."
            self.msg(channel, msg)

        #URL Fetchers & Integrated Utilities

        if msg == "!bbc":
            fd = feedparser.parse('http://feeds.bbci.co.uk/news/rss.xml?edition=int')
            description = fd.entries[0].description
            link = fd.entries[0].link
            fd = "\x02THE NEWS\x02: \x1D%s\x1D - \x02Read More\x02: %s" % (description, link)

            self.msg(channel, fd.encode('UTF-8'))

        if msg == "!bbc random":
            r = random.randint(0, 72)
            fd = feedparser.parse('http://feeds.bbci.co.uk/news/rss.xml?edition=int')
            description = fd.entries[r].description
            link = fd.entries[r].link
            fd = "\x02THE NEWS\x02: \x1D%s\x1D - \x02Read More\x02: %s" % (description, link)
            self.lineRate = 2

            self.msg(channel, fd.encode('UTF-8'))

        if msg.startswith("!t "):
            #Translates the source language into the target language

            gs = goslate.Goslate()

            wlist = msg.split(' ')

            slang = itemgetter(1)(wlist)
            tlang = itemgetter(2)(wlist)

            slangrep = '%s' % slang
            tlangrep = '%s' % tlang

            phrase = itemgetter(slice(3, None))(wlist)

            phrase_ = ' '.join(phrase)
            reply = gs.translate(phrase_, tlangrep, slangrep)

            self.msg(channel, reply.encode('UTF-8'))

        if msg.startswith("!dt "):
            #Translates the detected string to English

            gs = goslate.Goslate()

            wlist = msg.split(' ')

            trans = itemgetter(slice(1, None))(wlist)

            trans = ' '.join(trans)

            source = gs.detect(trans)
            reply = gs.translate(trans, 'en', source)

            self.msg(channel, reply.encode('UTF-8'))

        if msg.startswith("!qdb"):
            #This is lazy. It's unorthodox. Why do I use it? Because it works.
            #99.98% of the time, anyway.

            #TODO The above is unacceptable. Find another way to make it work.

            wlist = msg.split(' ')

            addend = itemgetter(1)(wlist)
            url = "http://www.arloria.net/qdb/%s" % addend
            msg = url
            self.msg(channel, msg)

        if msg == "!joke":
            #I hate this function. Why do I keep it?

            r = requests.get("http://api.icndb.com/jokes/random?")
            rj = r.json()
            msg = rj['value']['joke']
            self.msg(channel, msg.encode('utf-8', 'ignore'))

        # Misc

        if msg.startswith('!pornhub'):
            #For RadActiveLobstr.
            msg = "%s, I'm not that kind of bot." % user
            self.msg(channel, msg)

        if msg.startswith('!pronhub'):
            #For RadActiveLobstr.
            msg = "Did you mean !pornhub?"
            self.msg(channel, msg)

        if msg == "!help":
            msg = "Commands: !dance, !disconnect, !joke, !version, !info, !t [source lang] [target lang], !dt [foreign " \
                  "text], !qdb [number]"
            self.notice(user, msg)

        # Reminder

        if msg.startswith('!remind'):

            #Open the shelf
            sh = shelve.open('reminders')
            spl = msg.split(' ')

            #Get user, datetime, key(target) and data(reminder)
            _from = user
            timestamp = datetime.date.today()
            target = itemgetter(1)(spl)
            reminder = itemgetter(slice(2, None))(spl)
            reminder_ = ' '.join(reminder)

            #Alter data to include timestamp and user
            data = '(%s) %s reminds you... %s' % (timestamp, _from, reminder_)

            #Throw it into the shelf
            sh[target] = data
            msg = "I'll remind %s about that, %s" % (target, user)
            self.msg(channel, msg)

            if IndexError:
                pass

        if msg.__contains__(self.nickname and "reminder" or "Reminder" or "reminders" or "Reminders"):

            #Open shelf
            sh = shelve.open('reminders')
            rfor = user

            check = sh.has_key(rfor)

            if check is True:
                #Checks if key exists
                reminder = sh[rfor]
                reply = "[%s] %s" % (user, reminder)
                self.msg(channel, reply)

                #And deletes them
                del sh[rfor]

            elif check is False:
                pass

        if msg.startswith('.debugreminder'):
            sh = shelve.open('reminders')
            klist = sh.keys()
            print klist

    #IRC CALLBACKS

    #TODO Add more?

    def alterCollidedNick(self, nickname):
        return nickname + 'Clone'