# -*- coding: utf-8 -*-
"""
    args.py

    Provides common command line parsing for the lapmaster programs.

    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""

import os
import argparse

LOGFILE = 'log.csv'
CLASSFILE = 'classes.csv'
PERSONFILE = 'persons.csv'
TEAMFILE = 'teams.csv'

def enable_configdir_option(parser):
    parser.add_argument('-i', metavar='config_dir',
                        help='Directory in which to look for config files.',
                        default='.')

def enable_log_option(parser):
    parser.add_argument('-l', metavar='log_file', help='Log file to use.')

def enable_class_option(parser):
    parser.add_argument('-c', metavar='class_file',
                        help = 'Set class configuration file. ' \
                        'Default is config_dir/%s.' % (CLASSFILE))

def enable_person_option(parser):
    parser.add_argument('-p', metavar='person_file',
                        help = 'Set person configuration file. ' \
                        'Default is config_dir/%s.' % (PERSONFILE))

def enable_team_option(parser):
    parser.add_argument('-t', metavar='team_file',
                        help = 'Set team configuration file. ' \
                        'Default is config_dir/%s.' % (TEAMFILE))

def enable_output_option(parser):
    parser.add_argument('-o', metavar='dir',
                        help = 'Set an output directory for html result ' \
                        'files.',
                        default='.')

def get_options(parser):
    options = parser.parse_args()

    if hasattr(options, 'i') and options.i:
        options.c = options.i + os.sep + CLASSFILE
        options.p = options.i + os.sep + PERSONFILE
        options.t = options.i + os.sep + TEAMFILE
        if not hasattr(options, 'l') or options.l == None:
            options.l = options.i + os.sep + LOGFILE
        else:
            print(options.l)
            options.l = LOGFILE
    else:
        if not hasattr(options, 'l'):
            options.l = LOGFILE

    return options
