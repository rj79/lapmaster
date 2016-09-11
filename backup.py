#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    backup.py

    Backs up data with regular intervals so that another timekeeper computer
    can take over in case of failure in the primary computer.
    Works in tandem with restore.py.

    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""

import shutil
import sys
import time
import getopt
import os

files = ["log.csv", "classes.csv", "persons.csv", "teams.csv"]
backup_index = "backups.html"

interval = 30

def show_usage():
    print "Usage %s -o <output_dir> -i <interval>" % \
        (os.path.basename(sys.argv[0]))
    print "Makes backup of race data with regular intervals."
    print "An index of all backups (backups.html) is created in the output " + \
        "directory."
    print " -o\tWhere to place the backups. Usually the html directory."
    print " -i\tBackup interval in seconds. Default: " + str(interval)

def add_line(f, url, text):
    f.write("<tr>")
    f.write("<td>")
    f.write("<a href='%s'>%s</a>" % (url, text))
    f.write("</td>")
    f.write("</tr>")

def copy(src, dst):
    shutil.copyfile(src, dst)
    print "Copied %s to %s" % (src, dst)

try:
    opts, args = getopt.getopt(sys.argv[1:], "o:i:")
except getopt.GetoptError as err:
    show_usage()
    sys.exit(-1)

output = None
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

if output is None:
    print "Specify an output directory"
    show_usage()
    sys.exit(-1)

backups = []

for src in files:
    backups.append(src)

while True:
    stamp = time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime())
    print "Backup at %s" % (stamp)
    for src in files:
        dst = "%s/%s" % (output, src)
        copy(src, dst)

    for src in files:
        dst = "%s/%s_%s" % (output, stamp, src)
        url = "%s_%s" % (stamp, src)
        copy(src, dst)
        backups.append(url)

    with open("%s/%s" % (output, backup_index), "w") as f:
        f.write("<html><body><table>")
        for backup in reversed(backups):
            add_line(f, backup, backup)
        f.write("</table></body></html>")

    print "Waiting %d s" % (interval)

    try:
        time.sleep(interval)
    except KeyboardInterrupt:
        print "\nGot keyboard interrupt"
        break
