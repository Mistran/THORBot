__author__ = 'Platinum'

# Factory, launches and configures the bot and attaches it to the IRC network/channel.
# All settings can be configured in hammer.ini

import sys
import ConfigParser

from twisted.internet import protocol, reactor
from twisted.python import log

from thor import ThorBot


cfg = ConfigParser.RawConfigParser(allow_no_value=True)
cfg.read("magni.ini")

#TODO Summon Cthulhu and figure out why he broke my code
server = cfg.get('Connection', 'Server')
port = cfg.getint('Connection', 'Port')
__channels = cfg.get('Connection', 'Channels')


class ThorBotFactory(protocol.ClientFactory):
    protocol = ThorBot

    def __init__(self, channel):
        self.channel = channel

    def buildProtocol(self, addr):
        p = ThorBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        print "connection lost:", reason
        connector.connect()
        reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        print "failed to connect:", reason
        reactor.stop()

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    reactor.connectTCP(server, port, ThorBotFactory(__channels))
    reactor.run()