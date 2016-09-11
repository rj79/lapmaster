#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    makeconfig.py

    Generates a set of "blank" configuration files for a race that you can then
    by hand modify with registed participants.
    
    If you have a web based registration process, you likely want to create
    your own configuration file generator that uses your web registration as
    source. See the documentation for the format of the configuration files.

    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""

import os, sys

CLASSFILE='classes.csv'
PERSONFILE='persons.csv'
TEAMFILE='teams.csv'

MEN_SOLO=25
LADIES_SOLO=8
TEAM_3_MIXED=40
TEAM_3_LADIES=5
TEAM_6_MIXED=3

options = {'ms': MEN_SOLO,
           'ls': LADIES_SOLO,
           't3m': TEAM_3_MIXED,
           't3l': TEAM_3_LADIES,
           't6m': TEAM_6_MIXED}

descriptions = {'ms': "Men solo",
                "ls": "Ladies solo",
                "t3m": "Team 3 Mixed",
                "t3l": "Team 3 Ladies",
                "t6m": "Team 6 Mixed"}
bibs= []

def show_usage():
    print "Usage: %s [help] [ms=<count>] [ls=<count>] [t3m=<count>] [t3l=<count>] [t6m=<count>]" % (os.path.basename(sys.argv[0]))
    print "Class Meaning        Default"
    for k,v in descriptions.iteritems():
        print "{:<5} {:<14} {}".format(k, v, options[k])

if len(sys.argv) < 2:
    show_usage()
    sys.exit(-1)

error = False
for arg in sys.argv[1:]:
    if arg == "help":
        error = True
        break

    try:
        key, value = arg.split('=')
    except:
        error = True
        print "Could not interpret option %s" % (key)
        continue
    if key in options:
        try:
            options[key] = int(value)
        except:
            error = True
            print "Value of %s must be an integer" % (key)
            continue
    else:
        error = True
        print "Unknown option %s" % (key)
        continue

if error:
    show_usage()
    sys.exit(-1)

def classId(teamId):
    if teamId >= 101 and teamId <= 199:
        return 0
    if teamId >= 201 and teamId <= 299:
        return 1
    if teamId >= 301 and teamId <= 399:
        return 2
    if teamId >= 401 and teamId <= 499:
        return 3
    if teamId >= 601 and teamId <= 699:
        return 4

warning = False
for name in (CLASSFILE, PERSONFILE, TEAMFILE):
    if os.path.isfile(name):
        warning = True
        print "Warning! {} already exists!".format(name)

if warning:
    if raw_input("The above configuration files already exist. Do you really want to overwrite? [y/N]: ").upper() != "Y":
        print "Existing files untouched."
        sys.exit(-1)


for k,v in options.iteritems():
    print "{:<14}: {}".format(descriptions[k], v)

for i in range(101, 101 + MEN_SOLO):
    bibs.append(i)

for i in range(201, 201 + LADIES_SOLO):
    bibs.append(i)

for i in range(301, 301 + TEAM_3_MIXED):
    for m in range(1, 4):
        bibs.append(i * 10 + m)

for i in range(401, 401 + TEAM_3_LADIES):
    for m in range(1, 4):
        bibs.append(i * 10 + m)

for i in range(601, 601 + TEAM_6_MIXED):
    for m in range(1, 7):
        bibs.append(i * 10 + m)


with open(CLASSFILE, 'w') as f:
    f.write("0,1,Herr solo\n")
    f.write("1,1,Dam solo\n")
    f.write("2,3,Mixed 3\n")
    f.write("3,3,Dam 3\n")
    f.write("4,6,Mixed 6\n")
print "Created %s" % (CLASSFILE)

with open(PERSONFILE, 'w') as f:
    for i in bibs:
        if i < 1000:
            f.write("s,%d,%d,Person %d\n" % (classId(i), i, i))
        else:
            f.write("%d,Person %d\n" % (i, i))
print "Created %s" % (PERSONFILE)

teams = {}
for bib in bibs:
    if bib > 3010:
        teamId = bib / 10
        if not teamId in teams:
            teams[teamId] = []
        teams[teamId].append(bib)

with open(TEAMFILE, 'w') as f:
    for teamId in teams:
        text = "%d,Team %d" % (classId(teamId), teamId)
        for bib in teams[teamId]:
            text += ",%d" % (bib)
        text += "\n"
        f.write(text)

print "Created %s" % (TEAMFILE)
