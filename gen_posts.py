#!/usr/bin/env python
# coding: utf-8

"""
    Some very lazy python that reads an assortment of my bibtex files and
    processes them according to an arbitrary scheme wherein I am able to
    generate the posts based on metadata in the bibtex dbs.
"""

import codecs, unicodedata
import urllib, urllib2
import feedparser
import io, time, sys, re

from dateutil import parser


def get_as_bibtex (buf):
    return get_as_bibtex_no_regex(buf)


def get_as_bibtex_no_regex (buf):
    """
        Loads a string of lines as a dictionry consisting of relevant bibtex fields.
    """

    result = { 'raw': buf }

    t = 1
    while t < len(buf):
        k = [c.strip() for c in buf[t].split('=', 1)]
        
        if len(k) == 1:
            t = t + 1
            continue

        content = k[1].strip()

        while not (content.endswith('},') or content.endswith('}')):
            t = t + 1
            content = content + ' ' + buf[t].strip()

        key = k[0].strip('{},')
        content = content.strip('{},')

        result[key] = content

        t = t + 1
    
    return result
    

def parse_listings (lines):
    """
        Reads an entire bibtex file and returns a list of bibtex dictionaies.
    """

    listings = []

    collect = False
    inside_comment = False

    buf = []

    for line in lines:
        line = line.strip()
        if line.startswith("@comment"):
            if line.endswith("]"):
                continue

            inside_comment = True

        if line.startswith("%"):
            # Skip
            continue

        if line.startswith("@"):
            collect = True

        if collect:
            buf.append(line + '\n')

            if line == "}":
                collect = False

                if inside_comment:
                    inside_comment = False
                    buf = []
                    continue

                listings.append( get_as_bibtex(buf) )

                buf = []
        # collect

    return listings
# }}}


def clean (thing):
    return unicodedata.normalize('NFKD', thing.replace(':','&#58;')).encode('ascii', 'ignore')


def things (listings):
    count = 0
    start = 0
    to = len(listings)

    by_date = {}
    #
    for k in range(start, to):
        if "code" in listings[k] and listings[k]["code"] and ("ql" in listings[k]["code"].split(":")):
            pass
        else:
            continue

        if (not "ql_date" in listings[k]) or not (listings[k]["ql_date"]):
            continue

        dates = listings[k]["ql_date"].split(';')
        for date in dates:
            date = parser.parse(date).strftime("%Y-%m-%d")

            if date in by_date:
                by_date[date] += [listings[k]]
            else:
                by_date[date] = [listings[k]]
        #
    #

    for (k, listings) in by_date.iteritems():
        biblambda = lambda b: clean(b['raw'][0].split('{')[1].strip(',\r\n'))
        bibtexs = ", ".join([ biblambda(b) for b in listings ])
        filename = k + "-" + bibtexs + ".md"
        # print "Too busy", filename
        #
        print filename
        content = ""

        # for listing in listings:
        #     authors = listing['author']
        #     author  = clean(authors.split(' and ')[0])
        #     bibtex = biblambda(listing)
            
        # import pdb
        # pdb.set_trace()

        content = """---
published: true
layout: post
papers:
- %s
category: lunch
---
""" % "- ".join([ ("<a href='%s'>%s, %s</a>\r\n" % (l["url"],clean(l["title"]),biblambda(l))) for l in listings ])
        
        with open("_posts/%s" % filename, "w") as f:
            f.write(content)
    #
# }}}



if __name__ == "__main__": # {{{

    bibfiles = [
            '/home/noon/research/bibtex/misc.bib',
            '/home/noon/research/bibtex/quant.bib',
            '/home/noon/research/bibtex/math.bib',
            '/home/noon/research/bibtex/physics.bib',
        ]

    lines = []
    for bibfile in bibfiles:
        f = codecs.open(bibfile, "r", "utf-8")
        lines += f.readlines()

    listings = parse_listings(lines)
    things(listings)
