#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
   	top.py

	Generates list of top performances in a set of races. Outputs a set of
    CSV files that can be imported into a spreadsheet.

    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""

import lmcore
import args
import argparse
import os
import re

class JsObject(object):
	def __init__(self, *args, **kwargs):
		for arg in args:
			self.__dict__.update(arg)

		self.__dict__.update(kwargs)

	def __getitem__(self, name):
		return self.__dict__.get(name, None)

	def __setitem__(self, name, val):
		return self.__dict__.__setitem__(name, val)

	def __delitem__(self, name):
		if self.__dict__.has_key(name):
			del self.__dict__[name]

	def __getattr__(self, name):
		return self.__getitem__(name)

	def __setattr__(self, name, val):
		return self.__setitem__(name, val)

	def __delattr__(self, name):
		return self.__delitem__(name)

	def __iter__(self):
		return self.__dict__.__iter__()

	def __repr__(self):
		return self.__dict__.__repr__()

	def __str__(self):
		return self.__dict__.__str__()

def time_to_string(seconds):
    h = int(seconds) / 3600
    m = (int(seconds) - h * 3600) / 60
    s = int(seconds) - h * 3600 - m * 60
    return "%02d:%02d:%02d" % (h, m, s)

def load_result(logfile, report):
    if not os.path.isfile(logfile):
        return False
    for line in open(logfile, "r"):
        line = line.rstrip("\n\r")
        report.update(line)
    return True

# return best laps, excluding the first
def best_laps(info):
    laps = info.AllLaps[1:]
    best_laps = sorted(laps, key=lambda x: x[1])[:3]
    return best_laps

def get_personal_top(config, report):
    bibs = config.getPersonBibList()
    bib2info = {}
    for bib in bibs:
        teamId = report.Config.getTeamIdByBib(bib)
        lapInfoList = report.getLapInfoList(teamId)
        lap = 0
        if len(lapInfoList) > 0:
            for lapInfo in lapInfoList:
                lap += 1
                if lapInfo.Bib == bib:
                    if not bib in bib2info:
                        bib2info[bib] = JsObject()
                        bib2info[bib].Name = config.getPersonNameByBib(bib)
                        bib2info[bib].AllLaps = [(lap, lapInfo.LapTime)]
                    else:
                        bib2info[bib].AllLaps.append((lap, lapInfo.LapTime))

    summary = JsObject()
    summary.Data = []
    for bib, info in bib2info.iteritems():
        info.LapCount = len(info.AllLaps)
        info.BestLaps = best_laps(info)
        summary.Data.append(info)
    return summary

def write_file(path, text):
    with open(path, "w") as f:
        f.write(text)

def get_best_laps_per_person_csv(summary):
    text = '"Name","Lap count","Lap","Time","Lap","Time","Lap","Time"\n'
    for person in reversed(sorted(summary.Data, key=lambda x: x.LapCount)):
        text += '"%s",%d,' % (person.Name, person.LapCount)
        text += ",".join([ '%d,"%s"' % (info[0],
                                        time_to_string(info[1])) for info in person.BestLaps])
        text += "\n"
    return text

def get_best_laps_total_csv(summary):
    bestLaps = []
    for person in summary.Data:
        for lap in person.BestLaps:
            info = JsObject()
            info.Name = person.Name
            info.LapNumber = lap[0]
            info.Time = lap[1]
            bestLaps.append(info)

    text = '"Name","Lap number","Lap time"\n'
    for lap in sorted(bestLaps, key=lambda x: x.Time):
        text += '"%s",%d,"%s"\n' % (lap.Name, lap.LapNumber,
                                    time_to_string(lap.Time))
    return text

def find_dirs():
    dirs = []
    for entry in os.listdir('.'):
        if os.path.isdir(entry):
            m = re.match('(ml12h-20[\d]{2})', entry)
            if m:
                obj = JsObject()
                m = re.match('ml12h-(20[\d]{2})', entry)
                obj.Year = int(m.group(1))
                obj.Dir = entry
                dirs.append(obj)
    return dirs

def write_yearly_reports(summaries):
    for year in summaries.keys():
        write_file("%d_person_top.csv" % (year),
                   get_best_laps_per_person_csv(summaries[year]))
        write_file("%d_total_top.csv" % (year),
                   get_best_laps_total_csv(summaries[year]))

def get_summaries():
    dirs = find_dirs()
    summaries = {}
    for d in sorted(dirs, key=lambda x: x.Year):
        print "Processing %d in %s" % (d.Year, d.Dir)
        config = lmcore.loadConfig(d.Dir + "/classes.csv",
                                   d.Dir + "/persons.csv",
                                   d.Dir + "/teams.csv")
        if not config:
            sys.exit(1)

        report = lmcore.Report(config)
        if not load_result(d.Dir + "/log.csv", report):
            continue
        summaries[d.Year] = get_personal_top(config, report)
    return summaries

def find_all_persons_over_years(summaries):
    persons = set()
    for year in sorted(summaries.keys()):
        summary = summaries[year]
        for person in sorted(summary.Data, key=lambda x: x.Name):
            persons.add(person.Name)
    return list(persons)

def write_super_summary(summaries):
    persons = find_all_persons_over_years(summaries)

    text = "Name,"
    years = sorted(summaries.keys())
    for year in years:
        text += '"Laps %d","Best lap %d","Best time %d",' % (year, year, year)
    text += "\n"

    for person in sorted(persons):
        text += '"%s",' % (person)
        for year in years:
            participated = False
            for data in summaries[year].Data:
                if data.Name == person:
                    participated = True
                    text += "%d," % (data.LapCount)
                    if len(data.BestLaps) > 0:
                        text += '%d,"%s",' % (data.BestLaps[0][0],
                                              time_to_string(data.BestLaps[0][1]))
            if not participated:
                text += '"","","",'
        text += "\n"
    write_file("super_summary.csv", text)

summaries = get_summaries()
write_yearly_reports(summaries)
write_super_summary(summaries)
