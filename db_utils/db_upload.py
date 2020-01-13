#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    db_upload.py

    Uploads lap data to an online result system.

    :copyright: (c) 2016 by Dag Helstad.
    :license: BSD, see LICENSE for more details.
"""
from .db_base import *
import time
import re

def Usage():
    print('Usage: db_updload.py <-f input_file> <-u url> ' \
        '<-n node_id> <-i interval>')
    print('-f input_file\tRead laptime data from input_file')
    print('-u url\tURL of server')
    print('-n node_id\tNode ID of the race to upload data to')
    print('-i interval [s]\tThe interval of data upload')

def is_float(string):
    try:
        f = float(string)
        return True
    except ValueError:
        return False

class Uploader:
    def __init__(self, db, filename, interval):
        self.Db = db
        self.FileName = filename
        self.Interval = interval

    def _RewriteLine(self, line):
        '''This function rewrites a lapmaster / kickass_timer log file line to
        match the format expected by the server, i.e.
        [timestamp(s)]\t[<bib>|all]'''

        try:
            time, event = line.rstrip('\n').split(',')
        except:
            return None

        if event == "start all":
            event = 'all'

        if event != "all":
            if not is_float(event):
                return None

        if not is_float(time):
            return None

        return "%d\t%s" % (int(float(time)), event)

    def UploadLoop(self):
        Log('Starting')
        Log('Expecting LAPMASTER file format')

        while(True):
            try:
                self._upload()
                time.sleep(self.Interval)
            except KeyboardInterrupt:
                break

        Log("Exiting")

    def _upload(self):
        try:
            with open(self.FileName, 'r') as f:
                tweaked_lines = []
                for line in f:
                    l = self._RewriteLine(line)
                    if l != None:
                        tweaked_lines.append(l)

                data = '\n'.join([l for l in tweaked_lines])

                before = time.time()
                res = self.Db.UploadData(data)
                after = time.time()
                if int(res['deleted']) > 0 or len(res['added']) > 0:
                    Log("Uploaded data to server in %02fs" % (after - before))
                    Log("Removed: %d laps" % res['deleted'])
                    Log("Added:")
                    for added in res['added']:
                        Log("  %d\tat %s" % (int(added['bib']),
                                             time.strftime("%H:%M:%S",
                                                           time.localtime(float(added['passage'])))))
                if len(res['messages']) > 0:
                    for msg in res['messages']:
                        Log(msg)
        except xmlrpclib.Fault as error:
            Log('XMLRPC error: %d, %s' % (error.faultCode, error.faultString))
        except NetworkError:
            Log('Upload failed due to network error')
        except IOError as error:
            Log('File could not be read: %s' % error.strerror)


if __name__ == '__main__':
    file_name = ""
    url = ""
    node_id = -1
    interval = -1
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'f:u:n:i:hc')
        for o, a in opts:
            if o == '-f':
                file_name = a
            elif o == '-u':
                url = a
            elif o == '-n':
                node_id = int(a)
            elif o == '-i':
                interval = int(a)
            elif o == '-h':
                Usage()
    except getopt.GetoptError:
        print('Error in getopt.')
        sys.exit(1)
    except ValueError:
        Usage()
        sys.exit(1)

    if len(file_name) == 0 or len(url) == 0 or node_id == -1 or interval == -1:
        Usage()
        sys.exit(1)

    db = RemoteDB(url, '', node_id)
    uploader = Uploader(db, file_name, interval)
    uploader.UploadLoop()
