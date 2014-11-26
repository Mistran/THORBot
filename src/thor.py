#!/usr/bin/python


'''
THOR connects to an IRC network, joins a channel, and keeps a log of everything that goes on.
WolframAlpha integration will come later.
'''

# TWISTED Imports
from twisted.words.protocols import irc

# INTERNAL Imports
from modules import lists, news_fetcher, goslate, help

# SYS Imports
import random, shelve, datetime, os

# OTHER Imports
import ConfigParser, ctypes, threading, dataset, sys
from operator import itemgetter

# HTTP Handlers
import requests

versionName = "Magni"
versionEnv = "Python 2.7.3"

ctypes.windll.kernel32.SetConsoleTitleA("THORBot @ Valhalla")

cfg = ConfigParser.RawConfigParser(allow_no_value=True)
cfg.read("magni.ini")


class ThorBot(irc.IRCClient):
    """
    Primary IRC class. Controls just about everything that isn't a module.
    Below you'll find a bunch of options that are handled by hammer.ini.
    """

    def __init__(self):
        nickname = cfg.get('Bot Settings', 'Nickname')
        password = cfg.get('Bot Settings', 'NickPass')
        realname = 'Magni[THORBOT] @ VALHALLA'

        self.realname = realname
        self.nickname = nickname
        self.password = password
        self.lineRate = 1

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        print

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def irc_ERR_ERRONEUSNICKNAME(self, prefix, params):
        print "irc_ERR_ERRONEUSNICKNAME called"

    def irc_ERR_PASSWDMISMATCH(self, prefix, params):
        print "!!!INCORRECT PASSWORD!!!\n Check hammer.ini for the NICKPASS parameter"
        return

    #EVENTS

    def irc_unknown(self, prefix, command, params):

        ic = ["#jacoders", "#church_of_smek"]

        if command == "INVITE":
            if params[1] in ic[:]:
                return
            else:
                self.join(params[1])

    def signedOn(self):
        #Called when signing on
        print "Signed on successfully"
        self.join(self.factory.channel)

    def joined(self, channel):
        #Called when joining a channel
        print "Joined %s" % (channel)
        self.mode(self.nickname, True, "B")

    def userJoined(self, user, channel):
        print "%s has joined %s" % (user, channel)

    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]
        h = help.Helper
        approved = ["Serio", "Cat", "Mikey"]

        if msg == "!reload news":
            if user in approved:
                reload(news_fetcher)
                msg = "News Fetcher updated"
                self.msg(channel, msg)

            else:
                denied = "You are not authorized to use that command."
                self.msg(channel, denied)

        if msg == "!reload dict":
            if user in approved:
                reload(lists)
                msg = "Dictionaries updated"
                self.msg(channel, msg)

            else:
                denied = "You are not authorized to use that command."
                self.msg(channel, denied)

        #Debug
        if msg == ".debugcount weapons":
            count = len(lists.Randict.weapons)
            msg = "Weapons in Dictionary: %s" % count
            self.msg(channel, msg)

        if msg == ".debugcount shakespeare":
            count = len(lists.Randict.shakespeare)
            msg = "Shakespeare in Dictionary: %s" % count
            self.msg(channel, msg)

        if msg == ".debug reminder":
            sh = shelve.open('reminders')
            klist = sh.keys()
            print klist

        if msg == ".debug threads":
            t = threading
            print "CURRENT ACTIVE THREADS:" + t.activeCount()

        #List commands

        if msg.startswith("!slap"):
            slappee = msg.split(' ')
            slapped = itemgetter(slice(1, None))(slappee)
            sentence = ' '.join(slapped)

            #Randomizer
            weaponscore = random.choice(lists.Randict.weapons)

            #Post results
            attack = "\x02%s slapped %s with %s\x02" % (user, sentence, weaponscore)
            self.msg(channel, attack)

        if msg.startswith("!shakeit"):
            d = lists.Randict
            shake = random.choice(d.shakespeare)
            self.msg(channel, shake)

        #Dice Roll

        if msg == "!roll":
            dice = random.randint(1, 100)
            dice = str(dice)

            self.msg(channel, dice)

        #Help utilities

        if msg.startswith("!help"):
            wlist = msg.split(' ')
            note = itemgetter(1)(wlist)

            if note is "bbc":
                msg = h.bbc
                self.msg(channel, msg)

            if note is "roll":
                msg = h.roll
                self.msg(channel, msg)

            if note is "me":
                msg = h.me
                self.msg(channel, msg)

            if note is "t":
                msg = h.t
                self.msg(channel, msg)

            if note is "dt":
                msg = h.dt
                self.msg(channel, msg)

            if note is "qdb":
                msg = h.qdb
                self.msg(channel, msg)

        #URL Fetchers & Integrated Utilities

        if msg == "!bbc":
            b = news_fetcher.BBCNews_r
            self.lineRate = 2

            self.msg(channel, b.bbc_fd.encode('UTF-8'))

        if msg == "!bbc random":
            b = news_fetcher.BBCNews_r
            self.lineRate = 2

            self.msg(channel, b.bbcr_fd.encode('UTF-8'))

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

        if msg.startswith("!bash"):
            if msg == "!bash random":
                r = random.randint(1, 10000)
                url = "http://bash.org/?%s" % r
                self.msg(channel, url)

            else:

                wlist = msg.split(' ')

                addend = itemgetter(1)(wlist)
                url = "http://bash.org/?%s" % addend
                msg = url
                self.msg(channel, msg)

        if msg.startswith("!qdb"):
            #This is lazy. It's unorthodox. Why do I use it? Because it works.
            #99.98% of the time, anyway.

            #TODO The above is unacceptable. Find another way to make it work.

            if msg == "!qdb random":
                r = random.randint(1, 628)
                url = "http://qdb.v51.us/quote/%s" % r
                self.msg(channel, url)

            else:

                wlist = msg.split(' ')

                addend = itemgetter(1)(wlist)
                url = "http://qdb.v51.us/quote/%s" % addend
                msg = url
                self.msg(channel, msg)

        if msg == "!joke":
            #I hate this function. Why do I keep it?

            r = requests.get("http://api.icndb.com/jokes/random?")
            rj = r.json()
            msg = rj['value']['joke']
            self.msg(channel, msg.encode('utf-8', 'ignore'))

        if msg.startswith("!remind"):
            db = dataset.connect("sqlite:///valhalla.db/")
            tab = db['reminders']

            split = msg.split(' ')

            p1 = user

            target = itemgetter(1)(split)
            print target

            if target is "me".lower():
                target = p1
                pass

            count = itemgetter(3)(split)
            print count

            timer = itemgetter(4)(split)
            print timer

            remind = itemgetter(slice(5, None))(split)
            remind = ' '.join(remind)
            print remind

            if timer is "day".lower() or "days".lower():
                tab.insert(dict(p1=p1, p2=target, days=int(count), message=remind))
                pass

            elif timer is "hour".lower() or "hours".lower():
                tab.insert(dict(p1=user, p2=target, hours=int(count), message=remind))
                pass

            elif timer is "minute".lower() or "minutes".lower():
                tab.insert(dict(p1=user, p2=target, minutes=int(count), message=remind))
                pass

            elif timer is "second".lower() or "seconds".lower():
                tab.insert(dict(p1=user, p2=target, seconds=int(count), message=remind))
                pass

    #IRC CALLBACKS

    #TODO Add more?

    def alterCollidedNick(self, nickname):
        newnick = random.choice(lists.Randict.nicknames)
        return newnick
