#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    db_base.py

    Provides basic XML-RPC services for communication with a web-based
    system where participants can sign up for an event.

    :copyright: (c) 2016 by Dag Helstad.
    :license: BSD, see LICENSE for more details.
"""

import getopt
import sys
from datetime import datetime
import time
import xmlrpclib

def Log(msg):
    print '%s: %s' % (datetime.isoformat(datetime.now()), msg)
    pass

class NetworkError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return 'Network error'

class FileError(Exception):
    def __init__(self, descripton):
        self.descripton = descripton

    def __str__(self):
        return repr(self.descripton)

class RemoteDB:
    def __init__(self, url, password, race_id):
        self.server = xmlrpclib.ServerProxy('%s/xmlrpc.php' % url)
        self.race_id = race_id

    def UploadData(self, data):
        resp = self.server.ml12h_racetimer_upload_data(self.race_id, data)
        return resp

    def DeleteLaps(self):
        resp = self.server.ml12h_racetimer_delete_laps(self.race_id)
        return resp

    def GetRiders(self):
        resp = self.server.ml12h_racetimer_get_riders(self.race_id)
        return resp

    def SetRiderBib(self, rider_id, bib):
        resp = self.server.ml12h_racetimer_set_bib(self.race_id, rider_id, bib)
        return resp

    def GetTeamsRiders(self):
        resp = self.server.ml12h_racetimer_get_teams_riders(self.race_id)
        return resp

    def GetLaps(self):
        resp = self.server.ml12h_racetimer_get_laps(self.race_id)
        return resp
