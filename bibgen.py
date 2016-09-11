#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    bibgen.py

    Generates a PDF of bibs that can be printed, based on the race
    configuration files.

    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""

import math
import cairo
import poppler
import lmcore
import datetime
import sys
import getopt

today = datetime.date.today()
year = today.strftime('%Y')

A4_size_mm = [210.0, 297.0]

def mm_to_inch(iterable):
    return [i * 0.0393700787 for i in iterable]

def inch_to_point(iterable):
    return [i * 72.0 for i in iterable]

def print_text(ctx, text, size, x, y, scale, color):
    ctx.save()
    ctx.set_font_size(size)
    m = ctx.get_font_matrix()
    m.scale(scale[0], scale[1])
    ctx.set_font_matrix(m)
    ctx.move_to(x, y)
    ctx.set_source_rgb(color[0], color[1], color[2])
    ctx.show_text(text)
    ctx.restore()

def center_text(ctx, text, size, center, y, scale, color):
    ctx.save()
    ctx.set_font_size(size)
    m = ctx.get_font_matrix()
    m.scale(scale[0], scale[1])
    ctx.set_font_matrix(m)
    e = ctx.text_extents(text)
    x = center - e[2] / 2.0
    y -= e[1]
    x -= e[0]
    ctx.move_to(x, y)
    ctx.set_source_rgb(color[0], color[1], color[2])
    ctx.show_text(text)
    ctx.restore()

def add_logo(pageCtx, logoCtx):
    pass

WIDTH_MM = A4_size_mm[0]
HEIGHT_MM = A4_size_mm[1]

A4_size_points = inch_to_point(mm_to_inch(A4_size_mm))

WIDTH_POINTS = A4_size_points[0]
HEIGHT_POINTS = A4_size_points[1]

surface = cairo.PDFSurface('bibs.pdf', WIDTH_POINTS, HEIGHT_POINTS)

WIDTH = WIDTH_POINTS
HEIGHT = HEIGHT_POINTS

ctx = cairo.Context(surface)

ctx.scale(WIDTH, WIDTH)

def show_usage():
    print("Usage %s -b <text> -i <image>" % \
        (os.path.basename(sys.argv[0])))
    print("Generates bibs for printing.")
    print(" -b\tText to print on the back side of each bib")
    print(" -i\tImage to display on each bib. Must be in png format.")

try:
    opts, args = getopt.getopt(sys.argv[1:], "b:i:")
except getopt.GetoptError as err:
    show_usage()
    sys.exit(-1)

message = None
image_file = None

for o, a in opts:
    if o == '-b':
        message = a
    if o == '-i':
        image_file = a

def white_background():
    ctx.save()
    ctx.set_source_rgb(1.0, 1.0, 1.0)
    ctx.rectangle(0.0, 0.0, 1.0, math.sqrt(2.0))
    ctx.fill()
    ctx.restore()

def draw_cut_lines():
    ctx.save()
    ctx.set_source_rgb(0.0, 0.0, 0.0)
    ctx.set_dash([0.01, 0.01])
    ctx.set_line_width(0.002)

    height = math.sqrt(2)
    half_height = height / 2
    bib_height = 100.0 / WIDTH_MM
    bib_width =  186.0 / WIDTH_MM
    h_margin = (1.0 - bib_width) / 2

    ctx.move_to(0.0, half_height)
    ctx.line_to(1.0, half_height)

    ctx.move_to(0.0, half_height - bib_height)
    ctx.line_to(1.0, half_height - bib_height)

    ctx.move_to(0.0, half_height + bib_height)
    ctx.line_to(1.0, half_height + bib_height)

    ctx.move_to(h_margin, 0)
    ctx.line_to(h_margin, height)

    ctx.move_to(1.0 - h_margin, 0)
    ctx.line_to(1.0 - h_margin, height)

    ctx.stroke()
    ctx.restore()


ctx.select_font_face('Free Sans',
                     cairo.FONT_SLANT_NORMAL,
                     cairo.FONT_WEIGHT_BOLD)

white_background()
draw_cut_lines()

base_bib_y = 0.29
base_ml_y = 0.65
dy = 100.0 / WIDTH_MM

config = lmcore.configloader.loadConfig('classes.csv',
                                        'persons.csv',
                                        'teams.csv')

if config is None:
    print "Errors in configuration. PDF not created."
    sys.exit(1)

odd = True
count = 0

import os
pwd = os.getcwd()

image_surface = cairo.ImageSurface.create_from_png(image_file)

def create_backside(ctx, text):
    if text is None:
        return
    height = float(HEIGHT_MM) / float(WIDTH_MM)
    half = height / 2
    quarter = half / 2
    text_height = 0.05
    half_text_height = text_height / 2
    bib_height = 100.0 / WIDTH_MM
    center_text(ctx, text, text_height, 0.5, half - bib_height / 2 - half_text_height, [0.95, 1.0], [0, 0, 0])
    center_text(ctx, text, text_height, 0.5, half + bib_height / 2 - half_text_height, [0.95, 1.0], [0, 0, 0])
    surface.show_page()
    white_background()

for num in config.getPersonBibList():
    name = config.getPersonNameByBib(num)
    if odd:
        name_y = base_ml_y + 0.03
        bib_y = base_bib_y
        ml_y = base_ml_y
    else:
        name_y = base_ml_y + 0.03 + dy
        bib_y = base_bib_y + dy
        ml_y = base_ml_y + dy

    print_text(ctx, name, 0.02, 0.16, name_y, [1.1, 1.0], [0, 0, 0] )

    center_text(ctx, str(num), 0.36, 0.5, bib_y, [0.95, 1.0], [0, 0, 0])
    print_text(ctx, 'ML12h ' + str(year), 0.06, 0.16, ml_y, [1.1, 1.0],
                [0, 0, 0])

    ctx.save()
    ctx.identity_matrix()
    ctx.set_operator(cairo.OPERATOR_OVER)
    #ctx.scale(scale, scale)
    #logo_y = (ml_y) * 2398 * 4.0
    #ctx.translate(0, logo_y)
    scale = 0.06
    ctx.translate(0.58 * WIDTH_POINTS, 550 * ml_y)
    ctx.scale(scale, scale)
    #logo_y = (ml_y) * 2398 * 4.0
    ctx.set_source_surface(image_surface)
    ctx.paint()
    ctx.restore()

    odd = not odd
    count += 1
    if count % 2 == 0:
        surface.show_page()
        white_background()
        create_backside(ctx, message)
        draw_cut_lines()
