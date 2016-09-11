# -*- coding: utf-8 -*-
"""
    clazz.py

    Models a competition class, e.g. Men, Women, Juniors. Each class defines
    a maximum number of participants per team in that class.

    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""

class Class:
    def __init__(self, id, maxpersons, name):
        self.Id = id
        self.MaxPersons = maxpersons
        self.Name = name

    def isSolo(self):
        return self.MaxPersons == 1

    def __str__(self):
        return self.Name + " " + str(self.MaxPersons)
