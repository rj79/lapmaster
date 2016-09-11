# -*- coding: utf-8 -*-
"""
    person.py

    Models a person/participant in a competition.
    
    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""

class Person:
    def __init__(self, number, name):
        self.Number = int(number)
        self.Name = name

    def __cmp__(self, other):
        if self.Number < other.Number:
            return -1
        elif self.Number > other.Number:
            return 1
        else:
            return 0

    def __str__(self):
        return str(self.Number) + " " + self.Name
