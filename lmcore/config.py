# -*- coding: utf-8 -*-
"""
    config.py

    Functions for managing a race configuration.

    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""

class Config:
    def __init__(self, classes, persons, teams):
        self.Classes = classes
        self.Persons = persons
        self.Teams = teams

    def getClassIdList(self):
        return list(self.Classes.keys())

    def getClassNameById(self, classId):
        return self.Classes[classId].Name

    def getClassIdByBib(self, bib):
        teamId = self.getTeamIdByBib(bib)
        return self.Teams[teamId].ClassId

    def getClassIdByTeamId(self, teamId):
        return self.Teams[teamId].ClassId

    def getPersonBibList(self):
        bibList = []
        for k, person in self.Persons.items():
            bibList.append(person.Number)
        bibList.sort()
        return bibList

    def getPersonNameByBib(self, bib):
        return self.Persons[bib].Name

    def isSolo(self, bib):
        classId = self.getClassIdByBib(bib)
        return self.Classes[classId].isSolo()

    def isSoloTeam(self, teamId):
        classId = self.getClassIdByTeamId(teamId)
        return self.Classes[classId].isSolo()

    def getTeamIdList(self):
        return list(self.Teams.keys())

    def getTeamIdByBib(self, bib):
        for k, team in self.Teams.items():
            if team.isMember(bib):
                return team.Id

    def getTeamNameByBib(self, bib):
        for k, team in self.Teams.items():
            if bib in team.getBibList():
                return team.Name
        return None

    def getTeamNameByTeamId(self, id):
        for k, team in self.Teams.items():
            if team.Id == id:
                return team.Name
        return None

    def getTeamIdsInClass(self, classId):
        result = []
        for k, team in self.Teams.items():
            if team.ClassId == classId:
                result.append(team.Id)
        return result

    def getTeamBibsByBib(self, bib):
        result = []
        for k, team in self.Teams.items():
            if bib in team.getBibList():
                result = team.getBibList()
                break
        return result

    def getTeamBibsByTeamId(self, teamId):
        result = []
        for k, team in self.Teams.items():
            if teamId == team.Id:
                result = team.getBibList()
                break
        return result

    def getPerson(self):
        pass
