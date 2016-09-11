# -*- coding: utf-8 -*-
"""
    logger.py

    Manages logging.

    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.

    This module can be used to do basic logging and be used instead of
    print method. Logging can be done to stdout, a file or a custom logger.

    Example:
    from logger import Error, Note, Print
    Note("hello")

    Example if you want to mute output:
    import logger
    logger.logger = logger.NullLogger()
    logger.Note("hello")

    If you want to log to a file:
    import logger
    logger.logger = FileLogger('some_file.txt')
    logger.Note("hello")

    Or using your own custom logger class, which needs to implement methods
    called Error, Note and Print:
    import logger
    logger.logger = MyCustomLogger()
    logger.Note("hello")
"""

import sys
import os

def Error(msg):
    global logger
    logger.Error(msg)

def Note(msg):
    global Note
    logger.Note(msg)

def Print(msg):
    global logger
    logger.Print(msg)

class NullLogger:
    def Error(self, msg):
        pass

    def Note(self, msg):
        pass

    def Print(self, msg):
        pass

class BaseLogger:
    def _error(self, msg, f):
        f.write("Error: " + str(msg) + os.linesep)

    def _note(self, msg, f):
        f.write("Note: " + str(msg) + os.linesep)

    def _print(self, msg, f):
        f.write(str(msg) + os.linesep)

    def Error(self, msg):
        pass

    def Note(self, msg):
        pass

    def Print(self, msg):
        pass


class StdoutLogger(BaseLogger):
    def Error(self, msg):
        self._error(msg, sys.stdout)

    def Note(self, msg):
        self._note(msg, sys.stdout)

    def Print(self, msg):
        self._print(msg, sys.stdout)


class FileLogger(BaseLogger):
    def __init__(self, path):
        self.File = open(path, 'w')

    def __del__(self):
        self.File.close()

    def Error(self, msg):
        self._error(msg, self.File)

    def Note(self, msg):
        self._error(msg, self.File)


    def Print(self, msg):
        self._print(msg, self.File)


logger = StdoutLogger()

if __name__ == '__main__':
    for logger in [ FileLogger('test.log'), NullLogger(), StdoutLogger() ]:
        logger.Error('message')
        logger.Note('asdf')
        logger.Print('Just print')
