#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    restore.py

    Downloads configuration files and race results with regular intervals from
    the primary timekeeping computer, so that timekeeping can continue on a
    secondary computer in case of primary computer failure. Works in tandem
    with backup.py.

    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""

import urllib
import time
import getopt
import sys
import os
files = ["log.csv", "classes.csv", "persons.csv", "teams.csv"]

interval = 30
url_root = "http://localhost:5000/static"
output = "."

def show_usage():
    print "Usage %s -u <url> -o <output_dir> -i <interval>" % \
        (os.path.basename(sys.argv[0]))
    print "Restores race data."
    print " -u\tThe base url of the backup location. Default: " + url_root
    print " -o\tDirectory where to put the restored files. Default: " + output
    print " -i\tRestore interval in seconds. Default: " + str(interval)

try:
    opts, args = getopt.getopt(sys.argv[1:], "u:o:i:")
except getopt.GetoptError as err:
    show_usage()
    sys.exit(-1)

for o, a in opts:
    if o == '-o':
        output = a
        if not os.path.isdir(output):
            print "No such directory: " % (output)
            sys.exit(-1)
    if o == '-i':
        try:
            interval = max(1, int(a))
        except:
            pass
    if o == '-u':
        url_root = a

httpOpener = urllib.URLopener()

while True:
    ok = True
    for f in files:
        url = "%s/%s" % (url_root, f)
        dst = "%s/%s" % (output, f)
        try:
            httpOpener.retrieve(url, dst)
            print "Fetched %s" % (url)
        except IOError as err:
            ok = False
            print err

    print "For full list of backups see %s/backups.html" % (url_root)
    print "Waiting %d s" % (interval)
    try:
        time.sleep(interval)
    except KeyboardInterrupt:
        print "\nGot keyboard interrupt"
        break
