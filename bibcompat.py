# -*- coding: utf-8 -*-
"""
    bibcompat.py

    A little utility to provide compatibility with kickasstimer, a timekeeper
    written in perl that lapmaster was inspired by.

    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""

import os

class BibWriter:
    def __init__(self, logfile, output_dir):
        self.Logfile = logfile
        self.Bibfile = output_dir + os.sep + "bibtime.txt"

    def convertline(self, line):
        timestamp, event = line.rstrip('\n').split(',')
        timestamp = int(float(timestamp))
        event = event.replace('start all', 'all')
        return "%d\t%s\n" % (timestamp, event)

    def update(self):
        with open(self.Bibfile, "w") as bibfile:
            with open(self.Logfile, "r") as logfile:
                for line in logfile:
                    line = self.convertline(line)
                    bibfile.write(line)
