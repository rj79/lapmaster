#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    db_cmd.py

    Provides a command line interface to generate race configuration files
    based on an online participant sign up system.

    :copyright: (c) 2016 by Dag Helstad.
    :license: BSD, see LICENSE for more details.
"""

from .db_base import *
import os.path
import codecs

class Rider:
    def __init__(self, id, bib, name, team, team_nid):
        self.id = id
        self.bib = bib
        self.name = str(name)
        self.team = team
        self.team_nid = team_nid

    def __lt__(self, other):
        if self.team == other.team:
            return self.id < other.id
        else:
            return self.team < other.team

class TimeFormat:
    def __init__(self, timestamp):
        self.dt = datetime.fromtimestamp(timestamp)

    def long(self):
        return self.dt.isoformat()

    def short(self):
        return self.dt.strftime('%H:%M:%S')

class TimeDiffFormat:
    def __init__(self, timestamp):
        if timestamp < 0:
            self.neg = True
            self.dt = datetime.utcfromtimestamp(-timestamp)
        else:
            self.neg = False
            self.dt = datetime.utcfromtimestamp(timestamp)

    def short(self):
        neg = ''
        if self.neg:
            neg = '-'
        return neg + self.dt.strftime('%H:%M:%S')

class CmdDeleteLaps:
    @staticmethod
    def name():
        return "delete"

    @staticmethod
    def syntax():
        return ""

    @staticmethod
    def describe():
        return "Delete all laps for the race. Use with caution!"

    def __init__(self, db):
        self.db = db

    def execute(self, args):
        return self.db.DeleteLaps().__repr__()

class CmdDeleteBibs:
    @staticmethod
    def name():
        return 'deletebibs'

    @staticmethod
    def syntax():
        return ''

    @staticmethod
    def describe():
        return ("Unsets the bib number of all riders in the race. Use with caution!")

    def __init__(self, db):
        self.db = db

    def execute(self, args):
        for nid, data in self.db.GetTeamsRiders().items():
            if data['bib'] != '':
                Log('Delete bib for {}({})'.format(data['name'], data['bib']))
                db_res = self.db.SetRiderBib(nid, '')
        return ''

class CmdListRiders:
    @staticmethod
    def name():
        return 'riders'

    @staticmethod
    def syntax():
        return ''

    @staticmethod
    def describe():
        return 'Get all riders for this race.'

    def __init__(self, db):
        self.db = db

    def execute(self, args):
        res = self.db.GetTeamsRiders()
        riders = [Rider(nid, info['bib'], info['name'],
                        info['team_name'], info['team_nid'])
                  for nid, info in res.items()]

        header = '\nID\tBIB\tNAME(TEAM)\n=========================='
        rider_repr = ['%s\t%s\t%s (%s, %s)' % (r.id, r.bib, r.name, r.team, r.team_nid) for r in sorted(riders)]
        return '\n'.join([header] + rider_repr)

class CmdSetBib:
    @staticmethod
    def name():
        return 'setbib'

    @staticmethod
    def syntax():
        return '<id> <bib>'

    @staticmethod
    def describe():
        return ('Set the bib number to <bib> for the rider with id <id>. '
                'If no bib / id is given, then all unset riders are listed, '
                'with the option to set the bib.')

    def __init__(self, db):
        self.db = db

    def setSingleRider(self, id, bib):
        res = self.db.SetRiderBib(id, bib)
        return "Set rider bib for %s to %s" % (res['name'], res['bib'])

    def setAllRiders(self):
        dbParse = DbParse(self.db)
        res = self.db.GetTeamsRiders()
        riders = {nid : Rider(nid, info['bib'],
                              info['name'],
                              info['team_name'],
                              info['team_nid']) for nid, info in res.items()}

        for nid, r in sorted(riders.items()):
            if r.bib == '':
                print('Nid: {}, Rider: {}, Team: {}, Bib: {}'.format(nid, r.name,  r.team, r.bib))
                print('Propose bib: ', end=' ')
                resp = sys.stdin.readline().strip()
                try:
                    bib = int(resp)
                    self.setSingleRider(nid, bib)
                except ValueError:
                    pass

    def execute(self, args):
        if len(args) == 3:
            return self.setSingleRider(args[1], args[2])
        elif len(args) == 1:
            return self.setAllRiders()

class DbParse:
    def __init__(self, db):
        self.db = db
        self.riders = None

    def readDb(self):
        self.riders = self.db.GetTeamsRiders()
        # Fake a BIB number for all riders who have none set to make
        # files consistent
        for nid, rider in self.riders.items():
            if len(rider['bib']) == 0:
                self.riders[nid]['bib'] = -int(nid)
                Log("Warning: {} has no BIB ({}).".format(rider['name'], -int(nid)))

    def getPersons(self):
        if self.riders is None:
            self.readDb()
        return self.riders

    def getTeams(self):
        if self.riders is None:
            self.readDb()

        teams = {}

        # Create a dictionary for each team
        for rider in self.riders.values():
            if int(rider['class']) > 1:
                teams[rider['team_nid']] = {}
                teams[rider['team_nid']]['riders'] = []

        for nid, rider in self.riders.items():
            if int(rider['class']) > 1:
                teams[rider['team_nid']]['riders'].append(nid)
                teams[rider['team_nid']]['name'] = rider['team_name']
                teams[rider['team_nid']]['class'] = rider['class']

        return teams

    def getClasses(self):
        # This one's hard coded in the server...
        return ['0,1,Herr solo', '1,1,Dam solo', '2,3,Mixed 3', '3,3,Dam 3','4,6,Mixed 6']


class CmdCreateConfig:
    @staticmethod
    def name():
        return 'createconfig'

    @staticmethod
    def syntax():
        return '<directory>'

    @staticmethod
    def describe():
        return ('Reads teams and riders from the database and creates the '
                'classes.csv, persons.csv and teams.csv files. Note: '
                'overwrites the existing files.')

    def __init__(self, db):
        self.dbParse = DbParse(db)

    def createPersons(self):
        res = []
        for rider in self.dbParse.getPersons().values():
            if int(rider['class']) == 0 or int(rider['class']) == 1:
                # Solo rider
                res.append('s,{},{},{}'.format(rider['class'],
                                                rider['bib'],
                                                rider['name']))
            else:
                # Team rider
                res.append('{},{}'.format(rider['bib'],
                                           rider['name']))
        return sorted(res)

    def createTeams(self):
        teams = self.dbParse.getTeams()
        riders = self.dbParse.getPersons()

        res = []
        for team in teams.values():
            rider_bibs = [str(riders[r]['bib']) for r in team['riders']]
            if team['name'].find(',') != -1:
                Log("Warning: team name '{}' contains ','. "
                    "Removing ','.".format(team['name']))
            res.append('{},{},{}'.format(team['class'],
                                          team['name'].replace(',', ' '),
                                          ','.join(rider_bibs)))
        return res

    def createClasses(self):
        return self.dbParse.getClasses()

    def execute(self, args):
        if len(args) != 2:
            return "%s: Error, wrong number of arguments" % CmdCreateConfig.name()
        dirname = args[1]

        with codecs.open(dirname + '/persons.csv', 'w', 'utf-8') as f:
            f.write('\n'.join(self.createPersons()) + os.linesep)
        with codecs.open(dirname + '/teams.csv', 'w', 'utf-8') as f:
            f.write('\n'.join(self.createTeams()) + os.linesep)
        with codecs.open(dirname + '/classes.csv', 'w', 'utf-8') as f:
            f.write('\n'.join(self.createClasses()) + os.linesep)

        return 'Files written to directory {}.'.format(dirname)

class CmdProposeBib:
    @staticmethod
    def name():
        return 'proposebib'

    @staticmethod
    def syntax():
        return '[set]'

    @staticmethod
    def describe():
        return ("Finds riders with unset or strange bibs and "
                "proposes new numbers. If 'set' argument is given, "
                "command may set the numbers for you.")

    def __init__(self, db):
        self.db = db
        self.dbParse = DbParse(db)

    def checkSoloRiders(self, riders):
        res = []
        for classid, minbib, maxbib in [(0, 101, 199), (1, 201, 299)]:
            classriders = [ {'nid': int(nid), 'name': r['name'], 'current_bib': int(r['bib']),
                             'proposed_bib': '',  'reason': '' }
                            for nid, r in riders.items() if int(r['class']) == classid]
            used_bibs = [r['current_bib'] for r in classriders
                         if r['current_bib'] <= maxbib and r['current_bib'] >= minbib]
            bibs_to_use = [ i for i in range(maxbib, minbib-1, -1) if i not in used_bibs]

            for r in classriders:
                if r['current_bib'] < 0:
                    # bib < 0 means temporary bib, none in DB
                    r['proposed_bib'] = bibs_to_use.pop()
                    r['current_bib'] = ''
                    r['reason'] = 'No bib set in database'
                    res.append(r)
                elif r['current_bib'] < minbib or r['current_bib'] > maxbib:
                    r['proposed_bib'] = bibs_to_use.pop()
                    r['reason'] = 'bib number out of normal range for class'
                    res.append(r)

        return res

    def checkTeamRiders(self, riders, teams):
        # This function is wildly untested...
        res = []

        # Get all bib series in use, i.e. bib/10 >= 301
        used_series = {int(r['bib'])/10 for r in riders.values() if int(r['bib']) > 3010}
        used_bibs = {int(r['bib']) for r in riders.values()}

        for classid, min_x, max_x in [(2, 301, 399), (3, 401, 499), (4, 601, 699)]:
            classteams = [team for team in teams.values() if int(team['class']) == classid]
            series_to_use = [i for i in range(max_x, min_x-1, -1) if i not in used_series]
            for team in classteams:
                teambibs = [int(riders[nid]['bib']) for nid in team['riders'] if int(riders[nid]['bib']) > 0]
                if len(teambibs) == 0:
                    # No bibs were set; set all riders' bibs
                    s = series_to_use.pop()
                    for i, rider_nid in enumerate(team['riders']):
                        r = {}
                        r['current_bib'] = riders[rider_nid]['bib']
                        r['proposed_bib'] = s*10+i+1 # Ugh, this might propose a duplicate bib
                        r['nid'] = rider_nid
                        r['name'] = riders[rider_nid]['name']
                        r['reason'] = 'No rider in team had bib set'
                        res.append(r)
                else:
                    # At least one bib is set
                    team_series = {int(b)/10 for b in teambibs}
                    print(team_series)
                    if len(team_series) > 1:
                        # Uh-oh, something weird is going on. Giving up!
                        for rider_nid in team['riders']:
                            r = {}
                            r['current_bib'] = riders[rider_nid]['bib']
                            r['proposed_bib'] = -1
                            r['nid'] = rider_nid
                            r['name'] = riders[rider_nid]['name']
                            r['reason'] = "!!! Riders in team have different series. YOU figure it out, I can't"
                            res.append(r)
                    else:
                        s = team_series.pop()
                        team_free_bibs = [i for i in range(s*10+9, s*10, -1) if i not in teambibs]
                        for rider_nid in team['riders']:
                            r = {}
                            r['current_bib'] = riders[rider_nid]['bib']
                            r['nid'] = rider_nid
                            r['name'] = riders[rider_nid]['name']
                            if r['current_bib'] < 0:
                                r['proposed_bib'] = team_free_bibs.pop()
                                r['reason'] = "No bib set in database"
                                res.append(r)
        return res

    def formatBib(self, bib):
        if bib < 0:
            return '(none)'
        else:
            return bib


    def execute(self, args):
        if len(args) not in [1, 2]:
            return "%s: Error, wrong number of arguments" % CmdProposeBib.name()

        setBib = False
        if len(args) == 2:
            setBib = True

        teams = self.dbParse.getTeams()
        riders = self.dbParse.getPersons()

        proposed = self.checkSoloRiders(riders) + self.checkTeamRiders(riders, teams)

        if len(proposed) == 0:
            Log('No inconsistencies found.')
        else:
            Log('Found missing / strange bibs:')
            for r in proposed:
                # Arrgghhh!!! The data types are totally f***d up!
                teamname = riders[str(r['nid'])]['team_name']
                Log('{} ({}) #{}: proposed {}, {}'.format(r['name'],
                                                           teamname,
                                                           self.formatBib(r['current_bib']),
                                                           r['proposed_bib'],
                                                           r['reason']))
            if setBib:
                for r in proposed:
                    print(('Propose: Change bib of {} in '
                           'DB from {} to {}. Y/n?').format(r['name'],
                                                            self.formatBib(r['current_bib']),
                                                            r['proposed_bib']))
                    resp = sys.stdin.readline().strip()
                    if len(resp) == 0 or resp == 'y' or resp == 'Y':
                        db_res = self.db.SetRiderBib(r['nid'], r['proposed_bib'])
                        print("Rider bib for %s set to %s" % (r['name'], db_res['bib']))
                    else:
                        print("Skipping %s" % r['name'])

        return 'OK'

class LapParse:
    def __init__(self, db):
        self.db = db

    def getLaps(self):
        res = self.db.GetTeamsRiders()
        riders = {nid : Rider(nid, info['bib'],
                              info['name'],
                              info['team_name'],
                              info['team_nid']) for nid, info in res.items()}

        res = self.db.GetLaps()
        laps = []
        for l in res:
            rider = riders[l['rider_nid']]
            laps.append({'timestamp': int(l['timestamp']),
                         'bib': rider.bib,
                         'name': rider.name,
                         'team': rider.team,
                         'team_nid': rider.team_nid })
        return laps

class CmdGetLaps:
    @staticmethod
    def name():
        return 'getlaps'

    @staticmethod
    def syntax():
        return ''

    @staticmethod
    def describe():
        return ("Returns all laps stored for the race.")

    def __init__(self, db):
        self.db = db

    def execute(self, args):
        if len(args) != 1:
            return "%s: Error, wrong number of arguments" % CmdGetLaps.name()

        lp = LapParse(self.db)
        laps = lp.getLaps()
        laps_str = [ '{}\t{}\t{}\t{}'.format(TimeFormat(l['timestamp']).long(),
                                              l['bib'],
                                              l['name'],
                                              l['team']) for l in laps ]
        return '\n'.join(laps_str)

class CmdTrend:
    @staticmethod
    def name():
        return 'trend'

    @staticmethod
    def syntax():
        return 'teamnid_1 teamnid_2 ...'

    @staticmethod
    def describe():
        return ("Shows a list of relative times for each lap for the teams.")

    def __init__(self, db):
        self.db = db

    def execute(self, args):
        if len(args) < 3:
            return "%s: Error, wrong number of arguments" % CmdTrend.name()

        team_nid = args[1:]

        lp = LapParse(self.db)
        laps = lp.getLaps()

        # Create a list of tuples with
        # [(team_1_lap_1, team_2_lap_1, ...), (team_1_lap_2, ...)]
        ref_laps = [ ([l['timestamp'] for l in laps if l['team_nid'] == nid]) for nid in team_nid]
        team_laps = list(zip(*ref_laps))

        Log(team_laps.__repr__())

        # Now produce the output
        res = []
        res.append('\n\t' + '\t'.join([str(nid) for nid in team_nid]))

        if 1:
            # Time output
            for i,lap in enumerate(team_laps):
                diff = [TimeDiffFormat(l-lap[0]) for l in lap[1:]]
                res.append('{}\t{}\t'.format(i+1, TimeFormat(lap[0]).short()) +
                           '\t'.join([t.short() for t in diff]))
        else:
            #  Second output
            for i, lap in enumerate(team_laps):
                diff = [(l-lap[0]) for l in lap[1:]]
                res.append('{}\t{}\t'.format(i+1, 0) + '\t'.join([str(t) for t in diff]))
        return '\n'.join(res)


cmds = [ CmdDeleteLaps, CmdDeleteBibs, CmdListRiders, CmdSetBib,
         CmdCreateConfig, CmdProposeBib, CmdGetLaps, CmdTrend ]

def Usage():
    print('Usage: ka_cmd.py [-u url] [-n node_id] <command>')
    print('-u url\tURL of server')
    print('-n node_id\tNode ID of the race to upload data to')
    print('Commands:')

    for cmdclass in cmds:
        print('%s %s\t%s' % (cmdclass.name(), cmdclass.syntax(), cmdclass.describe()))


if __name__ == '__main__':
    url=''
    node_id=-1
    args = []

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'u:n:h')
        for o, a in opts:
            if o == '-u':
                url = a
            elif o == '-n':
                node_id = int(a)
            elif o == '-h':
                Usage()
                sys.exit(0)

    except getopt.GetoptError:
        print('Error in getopt.')
        sys.exit(1)
    except ValueError:
        Usage()
        sys.exit(1)

    if len(url) == 0 or node_id == -1 or len(args) == 0:
        Usage()
        sys.exit(1)

    Log('Starting')

    found = False
    for cmdclass in cmds:
        if cmdclass.name() == args[0]:
            found = True
            db = RemoteDB(url, '', node_id)
            try:
                cmd = cmdclass(db)
                Log(cmd.execute(args))
            except NetworkError:
                Log('Command failed due to network error')
            except xmlrpclib.Fault as error:
                Log('Server error: %d %s' % (error.faultCode, error.faultString))
            break
    if not found:
        Log("Unknown command '%s'" % args[0])
