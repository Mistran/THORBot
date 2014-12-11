#!/usr/bin/python


'''
THOR connects to an IRC network, joins a channel, and keeps a log of everything that goes on.
WolframAlpha integration will come later.
'''

# TWISTED Imports
from twisted.words.protocols import irc
from twisted.internet.defer import Deferred
from twisted.internet import defer
from twisted.python import log

# INTERNAL Imports
from modules import lists
from modules import help
from modules import news_fetcher
from modules import goslate
from modules.logger import Bin

# SYS Imports
import random

# OTHER Imports
import ConfigParser, ctypes, dataset
from operator import itemgetter

# HTTP Handlers
import requests

#COBE
from cobe.brain import Brain

versionName = "Magni"
versionEnv = "Python 2.7.3"

br = Brain('brain.brain')

ctypes.windll.kernel32.SetConsoleTitleA("THORBot @ Valhalla")

cfg = ConfigParser.RawConfigParser(allow_no_value=True)
cfg.read("magni.ini")


class ThorBot(irc.IRCClient):

    def __init__(self):
        nickname = cfg.get('Bot Settings', 'Nickname')
        password = cfg.get('Bot Settings', 'NickPass')
        realname = cfg.get('Bot Settings', 'Realname')

        self.realname = realname
        self.nickname = nickname
        self.password = password
        self.lineRate = 2
        self.teaserv = 0

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

        #Tells Magni to use the English COBE stemmer
        br.set_stemmer('english')

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
        teaserved = 0

        auth = cfg.get('Security', 'Authentication')

        self.logger = Bin(open(self.factory.filename, "a"))
        self.logger.log("%s" % msg)

        if msg.startswith("!tea"):
            l = msg.split(' ')
            u = itemgetter(1)(l)

            self.describe(channel, "serves %s with tea" % u)
            teaserved += 1
            state = "Tea served %s time(s)." % teaserved
            self.msg(channel, state)

        if msg:
            log.msg('[%s] <%s> %s' % (channel, user, msg))

            if self.nickname in msg:
                if user != "Smek":
                    msg = msg.split(self.nickname)
                    msg = ' '.join(msg)

                    r = br.reply(msg).encode('utf-8')
                    self.msg(channel, r)
                else:
                    return

            if msg.__contains__("gratis-handykarten"):
                return
            else:
                br.learn(msg)

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
            reload(news_fetcher)
            b = news_fetcher.BBCNews_r
            self.lineRate = 2

            self.msg(channel, b.bbc_fd.encode('UTF-8'))

        if msg == "!bbc random":
            reload(news_fetcher)
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

        if channel == self.nickname:
            #if msg == "!reboot %s" % auth:
            #    os.system('chariot.py')
            #    os._exit(1)
            if msg.startswith("!j %s" % auth):
                s = msg.split(' ')
                c = itemgetter(2)(s)
                self.join(c)
            if msg.startswith("!l %s" % auth):
                s = msg.split(' ')
                c = itemgetter(2)(s)
                self.leave(c)
            if msg.startswith("!k %s" % auth):
                s = msg.split(' ')
                c = itemgetter(2)(s)
                u = itemgetter(3)(s)
                r = itemgetter(slice(3, None))(s)
                r_ = ' '.join(r)
                self.kick(c, u, r_)
            if msg.startswith("!s %s" % auth):
                s = msg.split(' ')
                c = itemgetter(2)(s)
                m = itemgetter(slice(3, None))(s)
                m_ = ' '.join(m)
                self.msg(c, m_)

        if msg.startswith("!features"):
            reason = random.choice(lists.Randict.serio_is)
            msg = "Fuck that, Serio is %s" % reason
            self.msg(channel, msg)

    #IRC CALLBACKS

    #TODO Add more?

    def alterCollidedNick(self, nickname):
        newnick = random.choice(lists.Randict.nicknames)
        return newnick
