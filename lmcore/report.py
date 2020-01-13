# -*- coding: utf-8 -*-
"""
    report.py

    Aggregates results for a team or solo participant and keeps track of their
    results. In case of multi-lap events, it will keep track of result/standing
    in each lap.

    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""

import lmcore
from logger import Error, Note

# For transition for Python2
def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K:
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K


class LapInfo:
    def __init__(self):
        # The time at which the lap was registered
        self.PassTime = None
        # The number of the person that completed tha lap
        self.Bib = None
        # The lap time
        self.LapTime = None
        # The rank of the team when this lap was completed
        self.Rank = None
        # Lead time to next team in class. Unknown until the next team has
        # completed the same lap.
        # Is either a number of seconds, e.g. "73", or number of laps,
        # eg "4 laps"
        self.Lead = None
        # Id of next/worse/down team in class
        self.DownTeamId = None
        # Lag time behind the previous team in class. Not set for leaders.
        # Is either a number of seconds, e.g. "73", or number of laps,
        # eg "4 laps"
        self.Lag = None
        # Id of previous/better/up team in class
        self.UpTeamId = None

    def __str__(self):
        return '{"PassTime":%.2f, "Bib":%d, "LapTime":%.2f, "Rank":%d, ' \
          '"Lead":"%s" "Lag":"%s"}' % (self.PassTime, self.Bib, self.LapTime,
                                   self.Rank, str(self.Lead), str(self.Lag))

    def __repr__(self):
        return str(self)

class TeamInfo:
    def __init__(self, teamId):
        self.Id = teamId
        # List of LapInfo
        self.Laps = []
        # Current rank
        self.Rank = None

    def add_lap(self, startTime, timestamp, bib):
        lapInfo = LapInfo()
        lapInfo.PassTime = timestamp
        lapInfo.Bib = bib
        if len(self.Laps) == 0:
            lapInfo.LapTime = timestamp - startTime
        else:
            lapInfo.LapTime = timestamp - self.get_latest_pass_time()
        self.Laps.append(lapInfo)
        return self.Laps[-1]

    def get_rank(self):
        if len(self.Laps) > 0:
            return self.Laps[-1]
        return 0

    def get_latest_pass_time(self):
        if len(self.Laps) > 0:
            return self.Laps[-1].PassTime
        return 0

    def __str__(self):
        result = "Team={"
        result += "Id=" + str(self.Id) + \
            ", Laps=["
        for lap in self.Laps:
            result += str(lap) + ", "
        result += "]}"
        return result

class ClassInfo:
    def __init__(self, classId):
        self.Id = classId
        self.Teams = {}
        self.RankList = []

# Takes two TeamInfo
# Returns 1, 0 or -1 depending on if team1 is better, same or worse than
# team2.
def compareTeams(team1, team2):
    if len(team1.Laps) > len(team2.Laps):
        return -1
    elif len(team1.Laps) < len(team2.Laps):
        return 1
    else:
        if team1.get_latest_pass_time() < team2.get_latest_pass_time():
            return -1
        elif team1.get_latest_pass_time() > team2.get_latest_pass_time():
            return 1
        else:
            return 0

def time_to_string(time_in_seconds):
    return "%(minutes)02d:%(seconds)02d" \
        % {"minutes":int(time_in_seconds) / 60, "seconds":int(time_in_seconds) % 60}


class Report:
    def __init__(self, config):
        self.Config = config
        # Log only contains valid registered pairs of (timestamp, bib)
        self.Log = []
        # Mapping from classId to start time
        self.StartInfo = lmcore.StartInfo(config)
        # Mapping from classId to ClassInfo
        self.Classes = {}
        self.reset()

    def _get_team_info(self, teamId):
        classId = self.Config.getClassIdByTeamId(teamId)
        return self.Classes[classId].Teams[teamId]

    def _get_lap_list(self, teamId):
        classId = self.Config.getClassIdByTeamId(teamId)
        return self.Classes[classId].Teams[teamId].Laps

    def reset(self):
        self.Log = []
        self.StartInfo.reset()
        self.Classes = {}

        for classId in self.Config.getClassIdList():
            self.Classes[classId] = ClassInfo(classId)
            teamIdsInClass = self.Config.getTeamIdsInClass(classId)
            for teamId in teamIdsInClass:
                self.Classes[classId].Teams[teamId] = TeamInfo(teamId)

    # Parses one log line and updates report
    def update(self, logline):
        if len(logline) == 0:
            return

        timeText, event = logline.rstrip("\r\n").rsplit(",")
        try:
            timestamp = float(timeText)
        except:
            Error("Invalid timestamp %s" % timestamp)
            return False

        if event[0:5] == "start":
            classes = event[6:].rsplit(" ")
            self.StartInfo.startClasses(classes, timestamp)
        elif event.isdigit():
            bib = int(event)

            classId = self.Config.getClassIdByBib(bib)
            teamId = self.Config.getTeamIdByBib(bib)
            teamInfo = self._get_team_info(teamId)

            startTime = self.getStartTime(classId)
            if startTime == None:
                Note("Class has not yet started")
                return False

            # Register the lap
            newLap = teamInfo.add_lap(startTime, timestamp, bib)
            self.Log.append((timestamp, int(bib)))
            lapCount = len(teamInfo.Laps)

            # Now that the lap is registered, we can update current rank for all teams
            rankList = []
            rank = 1
            for t in sorted(iter(self.Classes[classId].Teams.values()), key=cmp_to_key(compareTeams)):
                if len(t.Laps) > 0:
                    t.Rank = rank
                    rank += 1
                rankList.append(t.Id)
            newLap.Rank = teamInfo.Rank

            rankIndex = teamInfo.Rank - 1
            self.Classes[classId].RankList = rankList

            # It is now also possible to calculate lag time behind the team
            # one position up
            # It is also possible to calculate the lead time of that team
            # to this team
            teamLapList = teamInfo.Laps
            # Special case if there is only one ranked team in the list to
            # avoid out of range errors in the rest of the code...
            if len(rankList) == 1:
                newLap.Lead = ""
                newLap.Lag = ""
            else:
                # Unless team is last team, we can calculate
                # * Lead time to the worse team
                if teamInfo.Rank < len(rankList):
                    worseTeamId = rankList[rankIndex + 1]
                    newLap.DownTeamId = worseTeamId
                    worseTeamLapList = self._get_lap_list(worseTeamId)
                    worseTeamLapCount = len(worseTeamLapList)
                    lapLead = lapCount - worseTeamLapCount - 1
                    if lapCount > 1:
                        if lapLead == 0:
                            diff = worseTeamLapList[lapCount - 2].PassTime \
                                - teamLapList[lapCount - 2].PassTime
                            # If the diff is negative, it means this team has
                            # passed one or more teams since last lap
                            if diff < 0:
                                newLap.Lead = "Plockar!"
                            else:
                                newLap.Lead = '(-' + time_to_string(diff) + ')'

                        else:
                            newLap.Lead = "-" + str(lapLead) + "v"

                # Unless team is leading team, we can calculate
                # * Lag time after the better team
                if teamInfo.Rank > 1:
                    betterTeamId = rankList[rankIndex - 1]
                    newLap.UpTeamId = betterTeamId
                    betterTeamLapList = self._get_lap_list(betterTeamId)
                    betterTeamLapInfo = betterTeamLapList[lapCount - 1]
                    if len(betterTeamLapList) == len(teamLapList):
                        diff =  teamLapList[lapCount - 1].PassTime \
                            - betterTeamLapList[lapCount - 1].PassTime
                        diffStr = time_to_string(diff)
                        newLap.Lag = "+" + diffStr
                        betterTeamLapInfo.Lead = "-" + diffStr
                    else:
                        lapDiff = len(betterTeamLapList) - len(teamLapList)
                        newLap.Lag = "+" + str(lapDiff) + "v"
                        betterTeamLapInfo.Lead = "-" + str(lapDiff) + "v"

        else:
            Error("Could not interpret log line: " + logline)
            return False

        # Everything went well
        return True

    # Returns a list of (time, bib) pairs of valid registered laps
    def getLapLog(self):
        return list(self.Log)

    # Returns an ordered list with teamIds sorted by rank. Best team first.
    def getTeamRankings(self, classId):
        return list(self.Classes[classId].RankList)

    def getTeamRanking(self, teamId):
        return self._get_team_info(teamId).Rank

    def getPreviousTeamRanking(self, teamId):
        laps = self._get_team_info(teamId).Laps
        if len(laps) < 2:
            return ""
        return laps[-2].Rank

    def getStartTime(self, classId):
        try:
            return self.StartInfo.getStartTime(classId)
        except KeyError:
            return None

    def getLastLapTime(self, teamId):
        lapList = self._get_lap_list(teamId)
        if len(lapList) > 0:
            return lapList[-1].LapTime
        return None

    # Returns a list of LapInfo
    def getLapInfoList(self, teamId):
        return self._get_lap_list(teamId)

    # Returns the LapInfo of the last lap of a team
    def getLastLapInfo(self, teamId):
        lapList = self._get_team_info(teamId).Laps
        if len(lapList) > 0:
            return lapList[len(lapList) - 1]
        return None

    # Returns the LapInfo of a team at a specific timestamp
    def getLapInfoByTimestamp(self, teamId, timestamp):
        if not teamId in self.Config.getTeamIdList():
            return None
        for lap in self._get_lap_list(teamId):
            if lap.PassTime == timestamp:
                return lap
        return None

    # Gets lapinfo by index. Index starts at 0
    def getLapInfoByIndex(self, teamId, index):
        if not teamId in self.Config.getTeamIdList():
            return None
        lapList = self._get_lap_list(teamId)
        if index >= 0 and index < len(lapList):
            return lapList[index]

        return None

    # Returns a list of (time, bib)
    def getLapList(self, teamId):
        result = []
        for lapInfo in self._get_lap_list(teamId):
            result.append((lapInfo.PassTime, lapInfo.Bib))

        return result

    # Returns the total number of laps of a person
    def getLapCountByBib(self, bib):
        teamId = self.Config.getTeamIdByBib(bib)

        laps = 0
        for lapInfo in self._get_lap_list(teamId):
            if lapInfo.Bib == bib:
                laps += 1
        return laps

    # Returns the total number of laps of a team
    def getLapCountByTeamId(self, teamId):
        return len(self._get_lap_list(teamId))

    # Returns a list of (lapTime, bib)
    def getLapTimes(self, teamId):
        result = []
        for lapInfo in self._get_lap_list(teamId):
            result.append((lapInfo.LapTime, lapInfo.Bib))

        return result

    # Returns the timestamp for a team's indexth lap
    def getLapTimeStamp(self, teamId, index):
        return self._get_lap_list(teamId)[index - 1]
