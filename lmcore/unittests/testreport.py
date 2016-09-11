# -*- coding: utf-8 -*-
"""
    testreport.py
    
    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""

import unittest
import report
import clazz
import team
import person
import config

START_TIME = 1354301000

# Class id
CID = 0

def create_team_with_info(teamId, laps, latest_pass_time):
    teamInfo = report.TeamInfo(teamId)
    for x in range(laps):
        teamInfo.add_lap(0, latest_pass_time, teamId)
    return teamInfo

class TestCompareTeams(unittest.TestCase):
    def test(self):
        resultA = create_team_with_info(0, 2, 2000)
        resultB = create_team_with_info(1, 2, 2001)
        resultC = create_team_with_info(2, 1, 1000)

        self.assertEqual(-1, report.compareTeams(resultA, resultB))
        self.assertEqual(1, report.compareTeams(resultB, resultA))
        self.assertEqual(1, report.compareTeams(resultC, resultA))
        self.assertEqual(1, report.compareTeams(resultC, resultB))
        self.assertEqual(0, report.compareTeams(resultA, resultA))

class TestReport(unittest.TestCase):
    def setUp(self):
        classes = {}
        classes[CID] = clazz.Class(CID, 1, 'Solo')
        persons = {}
        persons[1] = person.Person(1, 'Anna')
        persons[2] = person.Person(2, 'Bertil')
        persons[3] = person.Person(3, 'Carina')
        persons[4] = person.Person(4, 'David')
        teams = {}
        for p in persons.itervalues():
            teams[p.Number] = team.Team(CID, p.Name, [p.Number])
        self.config = config.Config(classes, persons, teams)
        self.Report = report.Report(self.config)

    def tearDown(self):
        pass

    def update(self, line):
        self.Report.update(line + "\n")

    def event(self, offset, what):
        self.update(str(START_TIME + offset) + "," + str(what))

    def start(self, what='all'):
        self.update(str(START_TIME) + ',start ' + str(what))

    def test_update_does_not_break_on_empty_line(self):
        self.Report.update("")

    def test_start_time_is_none_before_start(self):
        self.assertEqual(None, self.Report.getStartTime(CID))

    def test_start_time_is_set_after_start(self):
        self.start(CID)
        self.assertEqual(START_TIME, self.Report.getStartTime(CID))

    def test_team_that_does_first_lap_leads(self):
        self.start()
        self.event(1000, 4)
        self.assertEqual(4, self.Report.getTeamRankings(CID)[0])


    def test_team_that_does_second_lap_is_second(self):
        self.start()
        self.event(1000, 4)
        self.event(1001, 3)
        self.assertEqual([4, 3], self.Report.getTeamRankings(CID)[0:2])

    def test_simple_lead_lag_time(self):
        self.start()
        self.event(1000, 4)
        self.event(1001, 3)
        team4_info = self.Report.getLastLapInfo(4)
        team3_info = self.Report.getLastLapInfo(3)
        self.assertEqual("-00:01", team4_info.Lead)
        self.assertEqual("+00:01", team3_info.Lag)

    def test_preliminary_lead_time_when_same_team_was_behind_last_lap(self):
        self.start()
        self.event(1345274619, 1)
        self.event(1345274639, 2)
        team1_info = self.Report.getLastLapInfo(1)
        self.assertEqual("-00:20", team1_info.Lead)
        self.event(1345276137, 1)
        # This lead time is preliminary and is equal to last known lead time,
        # since the team below has not yet registered its corresponding lap.
        team1_info = self.Report.getLastLapInfo(1)
        self.assertEqual("(-00:20)", team1_info.Lead)
        self.event(1345276172, 2)
        team1_info = self.Report.getLastLapInfo(1)
        self.assertEqual("-00:35", team1_info.Lead)

    def test_preliminary_lead_time_when_surpassing_teams(self):
        self.start()
        self.event(100, 1)
        self.event(102, 2)
        self.event(104, 3)
        self.event(150, 2)

        team2_info = self.Report.getLastLapInfo(2)
        self.assertEqual("Plockar!", team2_info.Lead)
        self.assertEqual(1, self.Report.getTeamRanking(2))
        self.assertEqual(2, self.Report.getPreviousTeamRanking(2))

    def test_lead_time_when_more_than_one_lap_lead(self):
        self.start()
        self.event(1000, 4)
        self.event(1001, 3)
        self.event(1002, 4)
        self.event(1003, 4)
        team4_info = self.Report.getLastLapInfo(4)
        team3_info = self.Report.getLastLapInfo(3)
        self.assertEqual("-1v", team4_info.Lead)

    def test_getTeamRankings(self):
        self.start()
        self.event(1000, 4)
        self.event(1010, 3)
        self.event(1020, 1)
        self.event(1030, 4)
        self.event(1040, 4)
        self.event(1050, 1)
        self.event(1060, 1)
        self.assertEqual([4,1,3,2], self.Report.getTeamRankings(CID))
        self.event(1070, 1)
        self.assertEqual([1,4,3,2], self.Report.getTeamRankings(CID))
        self.event(1080, 2)
        self.event(1090, 2)
        self.assertEqual([1,4,2,3], self.Report.getTeamRankings(CID))

    def test_getTeamRanking(self):
        self.start()
        self.event(1000, 1)
        self.assertEqual(1, self.Report.getTeamRanking(1))

    def test_getLastLapTime(self):
        self.start()
        self.event(1000, 1)
        self.event(1010, 1)
        self.event(1021, 1)

        self.assertEqual(11, self.Report.getLastLapTime(1))
