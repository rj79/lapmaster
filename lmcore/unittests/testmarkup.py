# -*- coding: utf-8 -*-
"""
    testmarkup.py
    
    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""

import unittest
from markup import MarkupNode

class TestCompareTeams(unittest.TestCase):

    def test_short(self):
        m = MarkupNode('meta', "", True)
        self.assertEqual("<meta/>", str(m))

    def test_data(self):
        m = MarkupNode('p', "Hello")
        self.assertEqual("<p>Hello</p>\n", str(m))

    def test_add_child_no_data(self):
        m = MarkupNode('div')
        m.addChild('p')
        self.assertEqual("<div><p></p>\n</div>\n", str(m))

    def test_add_child_with_data(self):
        m = MarkupNode('div')
        m.addChild('p', 'Hello')
        self.assertEqual("<div><p>Hello</p>\n</div>\n", str(m))

    def test_add_child_short_no_data(self):
        m = MarkupNode('head')
        m.addChild('link', "", True)
        self.assertEqual("<head><link/></head>\n", str(m))

    def test_something(self):
        body = MarkupNode('body')
        head = body.addChild('head')
        link = head.addChild('link', "", True)
        link.setAttribute('rel', 'stylesheet')
        link.setAttribute('type', 'text/css')
        link.setAttribute('href', 'lapmaster.css');
