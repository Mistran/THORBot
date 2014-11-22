import feedparser
import random


class BBCNews_r():

            bbcr = random.randint(0, 70)
            bbcr_fd = feedparser.parse('http://feeds.bbci.co.uk/news/rss.xml?edition=int')
            bbcr_description = bbcr_fd.entries[bbcr].description
            bbcr_link = bbcr_fd.entries[bbcr].link
            bbcr_fd = "\x02THE NEWS\x02: \x1D%s\x1D - \x02Read More\x02: %s" % (bbcr_description, bbcr_link)

            bbc_fd = feedparser.parse('http://feeds.bbci.co.uk/news/rss.xml?edition=int')
            bbc_description = bbc_fd.entries[0].description
            bbc_link = bbc_fd.entries[0].link
            bbc_fd = "\x02THE NEWS\x02: \x1D%s\x1D - \x02Read More\x02: %s" % (bbc_description, bbc_link)