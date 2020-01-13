# -*- coding: utf-8 -*-
"""
    markup.py

    Utility for generating HTML. There are probably some better frameworks
    out there...
    Models a simple DOM node which can have attributes, children and data.

    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""
class MarkupNode:
    def __init__(self, tag, data=None, short=False):
        self.Tag = tag
        self.Short = short
        self.Attributes = {}
        self.Children = []
        self.Data = data

    def setAttribute(self, name, value):
        self.Attributes[name] = value;

    def setData(self, data):
        self.Data = data

    def addChild(self, tag, data=None, short=False):
        child = MarkupNode(tag, data, short)
        self.Children.append(child)
        return child

    def __str__(self):
        result = "<" + self.Tag

        if len(self.Attributes) > 0:
            for key, value in self.Attributes.items():
                result += " " + key + "=" + "\"" + value + "\""

        if self.Short:
            result += "/>"
            return result
        else:
            result += ">"

        if len(self.Children) > 0:
            for child in self.Children:
                result += str(child)
        elif self.Data:
            result += str(self.Data)

        result += "</" + self.Tag + ">\n"
        return result
