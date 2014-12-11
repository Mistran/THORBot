import ConfigParser

cfg = ConfigParser.RawConfigParser()
cfg.read("magni.ini")

logfile = cfg.get('Connection', 'Logfile')


class Bin:
    def __init__(self, fl):
        self.logfile = logfile
        self.fl = fl

    def log(self, message):
        self.fl.write('%s\n' % message)
        self.fl.flush()

    def close(self):
        self.fl.close()