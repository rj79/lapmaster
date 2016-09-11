# -*- coding: utf-8 -*-
"""
    team.py

    Models a team in a race. A team is associated with a class. depending on
    what class the team is associated with, it can have one or more members.

    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""

class Team:
    def __init__(self, classId, name, bibList):
        self.ClassId = classId
        self.Name = name
        self.BibList = bibList
        self.Id = min(self.BibList)

    def isMember(self, bib):
        return bib in self.BibList

    def getBibList(self):
        return list(self.BibList)

    def __cmp__(self, other):
        if self.Name < other.Name:
            return -1
        if self.Name > other.Name:
            return 1
        else:
            return 0

    def __str__(self):
        return self.Name
