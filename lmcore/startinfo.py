# -*- coding: utf-8 -*-
"""
    startinfo.py

    Keeps track of whether a particular class has started or not, and what the
    start time was.
    
    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""
import sys
import os
from logger import Error



class StartInfo:
    def __init__(self, config):
        self.Config = config
        self.StartTimes = {}

    def reset(self):
        self.StartTimes = {}

    def isStarted(self, classId):
        return classId in self.StartTimes

    # Sets start times for classes. Start of multiple classes may be requested
    # by passing a string with classIds separated by space.
    # Start times are only set if all requests were valid.
    # Returns true if star times were set, false otherwise
    def startClasses(self, classList, timestamp):
        startList = []

        if len(classList) == 0:
            Error("Need to specify which classes to start.")
            return False

        # Build the list of classes requested to start
        if "all" in classList:
            if len(classList) > 1:
                Error("\"all\" can not be used with any other class")
                return False

            for classId, clazz in self.Config.Classes.items():
                startList.append(classId)
        else:
            for classIdText in classList:
                if not classIdText.isdigit():
                    Error("Class id must be an integer or \"all\"")
                    return False
                classId = int(classIdText)
                if classId in self.Config.getClassIdList():
                    startList.append(classId)
                else:
                    Error("No class with id " + classIdText)
                    return False

        # Check that none of the requested classes have already started
        error = False
        for classId in startList:
            if classId in self.StartTimes:
                Error("Class " + str(classId) + ", \"" + \
                    self.Config.getClassNameById(classId) + \
                    "\" has already started.")
                error = True

        if error:
            return False

        # If everything was ok, start the requested classes
        for classId in startList:
            self.StartTimes[classId] = timestamp

        return True

    def getStartTime(self, classId):
        return self.StartTimes[classId]
