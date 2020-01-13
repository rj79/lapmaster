# -*- coding: utf-8 -*-
"""
    log.py

    Manages the log of events in a race.

    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""

import os
import time
from . import startinfo
try:
    import lockfile
except:
    print('Can not import lockfile. You need to either\n' \
    'apt-get install python-lockfile (Ubuntu) or\n' \
    'yum install python-lockfile (Fedora/RedHat/CentOS)')
    import sys
    sys.exit(1)

import socket
from .logger import Error, Note

ADDRESS = "localhost"
PORT = 8008
message_count = 0
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def isStart(event):
    return event[0:5] == 'start'

class ExclusiveLockFile():
    def __init__(self, path, access):
        self.Path = path
        self.Access = access
        self.Lock = lockfile.FileLock(path)
        self.File = None

    def __enter__(self):
        while not self.Lock.is_locked():
            try:
                self.Lock.acquire(timeout=3)
            except lockfile.LockTimeout:
                self.Lock.break_lock()
                self.Lock.acquire()

        self.File = open(self.Path, self.Access)
        return self.File

    def __exit__(self, type, value, traceback):
        self.File.close()
        self.Lock.release()

def loadLog(path, config):
    startInfo = startinfo.StartInfo(config)
    events = []
    row = 0
    if os.path.isfile(path):
        with ExclusiveLockFile(path, 'r') as f:
            while True:
                line = f.readline()
                row += 1
                if len(line) == 0:
                    break
                tokens = line.rstrip('\n').rsplit(',')

                try:
                    timestamp = float(tokens[0])
                except:
                    Error(path + ":" + str(row) + ": Invalid timestamp.")
                    return None, None

                if len(tokens[1]) == 0:
                    Note(path + ":" + str(row) + ": No event.")
#                    return None, None

                if isStart(tokens[1]):
                    classList = tokens[1].rsplit(" ")[1:]
                    if not startInfo.startClasses(classList, timestamp):
                        Error(path + ":" + str(row) + ": Invalid start.")
                        return None, None

                # Everything seems ok, add this entry to the log
                events.append((timestamp, tokens[1]))

    else:
        Note("Could not load log file " + path + ". Log is empty.")

    return Log(events), startInfo

def saveLog(log, path):
    global message_count
    with ExclusiveLockFile(path, 'w') as f:
        for e in log.Events:
            f.write(str(e[0]) + "," + str(e[1]) + "\n")
    sock.sendto(str(message_count), (ADDRESS, PORT))
    message_count += 1

class Log:
    def __init__(self, events):
        self.Events = events

    def __iter__(self):
        return LogIterator(self)

    def __len__(self):
        return len(self.Events)

    def __getitem__(self, index):
        return self.Events[index]

    def __cmp__(self, other):
        if other == None:
            return 1

        if len(self.Events) > len(other.Events):
            return 1
        elif len(self.Events) < len(other.Events):
            return -1
        else:
            if len(self.Events) == 0:
                return 0
            lastIndex = len(self.Events) - 1
            if self.Events[lastIndex][0] < other.Events[lastIndex][0]:
                return 1
            elif self.Events[lastIndex][0] > other.Events[lastIndex][0]:
                return -1
            else:
                return 0

    def is_valid_index(self, index):
        return index >= 0 and index < len(self.Events)

    def clear(self):
        self.Events = []

    def append(self, time, event):
        self.Events.append((time, event))

    def is_start(self, index):
        return isStart(self.Events[index][1])

    def set(self, index, event):
        if not self.is_valid_index(index):
            Error("Index out of range")
            return

        if isinstance(index, str):
            if not index.isdigit():
                raise KeyError("Index must represent an integer")

        if not isinstance(index, int):
            raise KeyError("Index must represent an integer")

        i = int(index)
        time = self.Events[i][0]
        self.Events[i] = (time, event)

    def tail(self, count):
        size = len(self.Events)
        index = size - int(count)
        result = Log([])
        if index < 0:
            index = 0
        text = ""
        for e in self.Events[index:]:
            result.Events.append(e)
            index += 1
        return result

    def __str__(self):
        result = ""
        for entry in self.Events:
            result += str(entry[0]) + "," + entry[1] + "\n"
        return result

class LogIterator:
    def __init__(self, log):
        self.Log = log
        self.Index = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            result = list(self.Log.Events[self.Index])
            self.Index += 1
            return result
        except IndexError:
            raise StopIteration
