# -*- coding: utf-8 -*-
"""
    teststartinfo.py
    
    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""

import unittest
import startinfo
import clazz
import person
import team
import config
import logger

CID_SOLO = 1
CID_TEAM = 2

class TestStartInfo(unittest.TestCase):
    def setUp(self):
        classes = {}
        classes[CID_SOLO] = clazz.Class(CID_SOLO, 1, 'Solo')
        classes[CID_TEAM] = clazz.Class(CID_TEAM, 2, 'Team')
        persons = {}
        # Solo
        persons[11] = person.Person(11, 'Anna S')
        persons[12] = person.Person(12, 'Bertil S')
        persons[13] = person.Person(13, 'Carina S')
        persons[14] = person.Person(14, 'David S')
        # Team
        persons[21] = person.Person(21, 'Alva T')
        persons[22] = person.Person(22, 'Anders T')
        persons[31] = person.Person(31, 'Berit T')
        persons[32] = person.Person(32, 'Bastian T')
        persons[41] = person.Person(41, 'Christine T')
        persons[42] = person.Person(42, 'Carl T')

        teams = {}

        for x in range(11, 15):
            p = persons[x]
            teams[p.Number] = team.Team(CID_SOLO, p.Name, [p.Number])

        teams[21] = team.Team(CID_TEAM, p.Name, [21, 22])
        teams[31] = team.Team(CID_TEAM, p.Name, [31, 32])
        teams[41] = team.Team(CID_TEAM, p.Name, [41, 42])

        conf = config.Config(classes, persons, teams)
        logger.logger = logger.NullLogger()
        self.StartInfo = startinfo.StartInfo(conf)

    def test_is_not_started_before_start(self):
        self.assertFalse(self.StartInfo.isStarted(CID_SOLO))
        self.assertFalse(self.StartInfo.isStarted(CID_TEAM))

    def test_start_only_one_class(self):
        self.StartInfo.startClasses([str(CID_SOLO)], 11)
        self.assertTrue(self.StartInfo.isStarted(CID_SOLO))
        self.assertFalse(self.StartInfo.isStarted(CID_TEAM))
        self.assertEqual(11, self.StartInfo.getStartTime(CID_SOLO))

    def test_start_class_list(self):
        self.StartInfo.startClasses([str(CID_TEAM), str(CID_SOLO)], 22)
        self.assertTrue(self.StartInfo.isStarted(CID_SOLO))
        self.assertTrue(self.StartInfo.isStarted(CID_TEAM))
        self.assertEqual(22, self.StartInfo.getStartTime(CID_TEAM))
        self.assertEqual(22, self.StartInfo.getStartTime(CID_SOLO))

    def test_start_none_fails(self):
        self.assertFalse(self.StartInfo.startClasses([''], 0))

    def test_start_all(self):
        self.StartInfo.startClasses(['all'], 33)
        self.assertTrue(self.StartInfo.isStarted(CID_SOLO))
        self.assertTrue(self.StartInfo.isStarted(CID_TEAM))
        self.assertEqual(33, self.StartInfo.getStartTime(CID_TEAM))
        self.assertEqual(33, self.StartInfo.getStartTime(CID_SOLO))

    def test_can_not_start_class_twice(self):
        self.StartInfo.startClasses([str(CID_SOLO)], 33)
        self.assertFalse(self.StartInfo.startClasses([str(CID_SOLO)], 44))
        self.assertEqual(33, self.StartInfo.getStartTime(CID_SOLO))

    def test_start_all_must_be_single_argument(self):
        self.assertFalse(self.StartInfo.startClasses([str(CID_SOLO), 'all'], 33))
        self.assertFalse(self.StartInfo.isStarted(CID_SOLO))
