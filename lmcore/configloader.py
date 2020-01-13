# -*- coding: utf-8 -*-
"""
    configloader.py

    Loads race configuration from files and performs sanity checking before
    returning a config object.
    
    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""

import os
from .clazz import Class
from .person import Person
from .team import Team
from .config import Config
from .logger import Error, Note, Print

class ConfigLoader:
    def __init__(self, classesFile, personsFile, teamsFile):
        self.ClassConfig = classesFile
        self.PersonConfig = personsFile
        self.TeamConfig = teamsFile

        self.Classes = {}
        self.Persons = {}
        self.Teams = {}

        self.File = ""
        self.Row = 0

    def error(self, message):
        Error("%s: %d: %s" % (self.File, self.Row, message))

    def isValidPerson(self, bib):
        if bib in self.Persons:
            self.error("There is already a person with number " + str(bib))
            return False
        return True

    def isValidTeam(self, classId, name, bibList):
        # Check for valid class
        if not classId in self.Classes:
            self.error(self.TeamConfig, self.TeamConfig,
                       "No class with id " + str(classid) + " is defined.")
            return False

        # Check for unique team name
        for k, team in self.Teams.items():
            if name == team.Name:
                self.error("There is already a team called " + name)
                return False

        # Check for member list consistency
        members = []
        for bibText in bibList:
            bib = int(bibText)

            if not bib in self.Persons:
                self.error("There is no person with number "
                           + str(bib))
                return False

            for b in members:
                if bib == b:
                    self.error("Person with number " + str(bib) \
                                   + " is already in team.")
                    return False

            for teamId, team in self.Teams.items():
                for b in team.BibList:
                    if bib == b:
                        self.error("Person with number "
                                   + str(bib) + " is already in "
                                   "another team.")
                        return False
            members.append(bib)

        return True

    def showClassFormat(self):
        Print("Class definition format should be:"\
              " <class id>,<max team size>,<class name>")
        Print("Examples:")
        Print("2,1,Ladies solo")
        Print("3,6,Six Persons Mixed")

    def loadClasses(self):
        self.File = self.ClassConfig

        if not os.path.isfile(self.ClassConfig):
            Error("Can not find " + self.ClassConfig)
            return False

        self.Row = 0
        for line in open(self.ClassConfig, 'r'):
            self.Row += 1
            tokens = line.rstrip('\n').rsplit(',')
            try:
                classid = int(tokens[0])
                maxpersons = int(tokens[1])
                name = tokens[2]
            except ValueError:
                self.error("Wrong class format.")
                self.showClassFormat()
                return None

            if classid in self.Classes:
                self.error("There is already a class with number " \
                               + str(classid))
                return False
            for n, c in list(self.Classes.items()):
                if c.Name == name:
                    self.error("There is already a class with name " \
                                   + name)
                    return False
            self.Classes[classid] = Class(classid, maxpersons, name)
        return self.Classes

    def loadPersons(self):
        self.File = self.PersonConfig

        if not os.path.isfile(self.PersonConfig):
            Error("Can not find " + self.PersonConfig)
            return False

        self.Row = 0
        for line in open(self.PersonConfig, 'r'):
            self.Row += 1
            if line == '\n':
                continue
            tokens = line.rstrip('\n').lstrip().rsplit(',')
            if len(tokens) < 2:
                return False
            # Ignore comments
            if tokens[0][0] == '#':
                continue

            if tokens[0] == "s":
                if len(tokens) < 4:
                    self.error("Solo person format: s,<class>,<bib>,<name>")
                    return False

                # Solos have class info on the same line
                classId = int(tokens[1])
                bib = int(tokens[2])
                name = tokens[3]

                if self.isValidPerson(bib):
                    self.Persons[bib] = Person(bib, name)

                if self.isValidTeam(classId, name, [bib]):
                    team = Team(classId, name, [bib])
                    teamId = team.Id
                    self.Teams[teamId] = team
            else:
                if len(tokens) != 2:
                    self.error("Team person format: <bib>,<name>")
                    return False
                bib = int(tokens[0])
                if not self.isValidPerson(bib):
                    return False
                self.Persons[bib] = Person(bib, tokens[1])
        return self.Persons

    def loadTeams(self):
        self.File = self.TeamConfig

        if not os.path.isfile(self.TeamConfig):
            Note("Can not find " + self.TeamConfig)
            return self.Teams

        self.Row = 0
        for line in open(self.TeamConfig, 'r'):
            self.Row += 1
            if line == '\n':
                continue
            tokens = line.rstrip('\n').rsplit(',')
            if len(tokens) < 2:
                return False

            classId = int(tokens[0])
            name = tokens[1]

            clazz = self.Classes[classId]
            if len(tokens[2:]) > clazz.MaxPersons:
                self.error("Too many members in team.")
                return False

            if self.isValidTeam(classId, name, tokens[2:]):
                team = Team(classId, name, [int(bib) for bib in tokens[2:]])
                teamId = team.Id
                self.Teams[teamId] = team

        return self.Teams

    def __str__(self):
        text = "Classes\n"
        for n, c in self.Classes.items():
            text += str(n) + "\t" + str(c) + '\n'
        text += "\nPersons\n"
        for k in sorted(self.Persons.keys()):
            text += str(k) + "\t" + str(self.Persons[k].Name) + '\n'
        text += "\nTeams\n"
        for k in sorted(self.Teams.keys()):
            text += str(self.Teams[k]) + '\n'
        return text

def check(classes, persons, teams):
    # See if there is a person which is not in a team
    status = True
    for personId, p in persons.items():
        member = False
        for teamId, t in teams.items():
            if t.isMember(p.Number):
                member = True
                break
        if not member:
            Error("Person " + str(p.Number) + " " \
                      + str(p.Name) + " is not in any team")
            status = False
    return status

def loadConfig(classesFile, personsFile, teamsFile):

    if classesFile == None:
        classesFile = 'classes.csv'
    if personsFile == None:
        personsFile = 'persons.csv'
    if teamsFile == None:
        teamsFile = 'teams.csv'

    loader = ConfigLoader(classesFile, personsFile, teamsFile)

    classes = loader.loadClasses()
    if not classes:
        Error("Could not load " + classesFile)
        return None

    persons = loader.loadPersons()
    if not persons:
        Error("Could not load " + personsFile)
        return None

    teams = loader.loadTeams()
    if not teams:
        Error("Could not load " + teamsFile)
        return None

    if not check(classes, persons, teams):
        return None

    return Config(classes, persons, teams)
