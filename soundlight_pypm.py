#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# SoundLight project 2014
# Designer: Dalma Kadocsa
# dalmoca@gmail.com
#
# Developer: Zsombor Hollay-Horváth
# hbotondzs@gmail.com
#
# Special thanks to John Harrison on pyportmidi project

import gtk
import gobject
import math
from time import strftime as timecode

from pygame import pypm

class shape:
  def __init__(self, args):

    self.done         = True
    self.on_begin     = False
    self.on_end       = False
    self.size_multip  = 1.0
    self.alpha_multip = 1.0

    self.type = args["type"]
    if self.type == "circle":
      self.center = [0.0, 0.0]
      if "center" in args:
        self.center = self.conv_center(args["center"])
      self.angle = [0.0, math.pi*2]
      if "angle" in args:
        self.angle = self.conv_angle(args["angle"])
      self.size   = self.conv_size(args['size'])
    elif self.type == "rectangle":
      raise NotImplementedError
    else:
      raise TypeError
    if args["fill"]:
      self.fill = True
      self.fill_color = self.conv_color(args['fill']['color'])
    else:
      self.fill = False
    if args["line"]:
      self.line = True
      self.line_width = self.conv_line_width(args['line']['width'])
      self.line_color = self.conv_color(args['line']['color'])

  def conv_color(self, c):
    if len(c) == 6:
      return (int(c[0:2],16)/255.0, int(c[2:4],16)/255.0, int(c[4:6],16)/255.0, 1.0)
    elif len(c) == 8:
      return (int(c[0:2],16)/255.0, int(c[2:4],16)/255.0, int(c[4:6],16)/255.0, int(c[6:8],16)/255.0)

  def conv_center(self, i):
    return [float(i[0]), float(i[1])]

  def conv_angle(self, i):
    return [i[0]/180.0*math.pi, i[1]/180.0*math.pi]

  def conv_size(self, i):
    return float(int(i)/100.0)

  def conv_line_width(self, i):
    return float(i)

  def begin_on_anim(self):
    self.size_multip  = 1.0
    self.alpha_multip = 0.1
    self.on_begin     = True
    self.on_end       = False
    self.done         = False

  def begin_off_anim(self):
    self.on_begin = False
    self.on_end   = True

  def draw(self, cr, w, h):
    if self.type == "circle":
      if w > h:
        b = h
      else:
        b = w
    if self.line:
      color = list(self.line_color)
      color[3] *= self.alpha_multip
      cr.set_source_rgba(*color)
      cr.set_line_width(self.line_width)
      cr.arc((w/2)+(w*self.center[0]), (h/2)+(h*self.center[1])*-1, b*self.size/2*self.size_multip, self.angle[0], self.angle[1])
      cr.stroke()
    if self.fill:
      color = list(self.fill_color)
      color[3] *= self.alpha_multip
      cr.set_source_rgba(*color)
      cr.arc((w/2)+(w*self.center[0]), (h/2)+(h*self.center[1])*-1, b*self.size/2*self.size_multip, self.angle[0], self.angle[1])
      cr.close_path()
      cr.fill()

    # Dalmus! Ezeket állítsd!

    # Mennyit nő a cucc
    max_size        = 1.2

    # Milyen gyorsan nő
    size_speed      = 0.02

    # Milyen gyorsan fényesedik
    alpha_on_speed  = 0.1

    # Milyen lassan veszti a fényerőt
    alpha_off_speed = 0.04


    if self.on_begin:
      if self.alpha_multip < 1.0:
        self.alpha_multip += alpha_on_speed
      if self.size_multip < max_size:
        self.size_multip += size_speed
      if self.alpha_multip >= 1.0 or self.size_multip >= max_size:
        self.on_begin     = False
        self.begin_off_anim()
    if self.on_end:
      if self.alpha_multip > 0.0:
        self.alpha_multip -= alpha_off_speed
        self.size_multip  += size_speed
      else:
        self.alpha_multip = 0.0
        self.on_end       = False
        self.done         = True

class note:
  def __init__(self, args):
    self.shape = []
    for i in args:
      self.shape.append(shape(i))

  def switch(self, pos):
    # Switch on
    if pos:
      for i in self.shape:
        i.begin_on_anim()
    else:
      for i in self.shape:
        i.begin_off_anim()

  def draw(self, cr, w, h):
    on = False
    for i in self.shape:
      if not i.done:
        on = True
    if not on:
      return
    for i in self.shape:
      i.draw(cr, w, h)


def calc_chord(n):
  return (["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"])[(n+3)%12]+str(n/12-1)

def read_keys():

  return {
  "A0":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 100,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "A#0":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 99,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "B0":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 98,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "C1":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 97,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "C#1":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 96,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "D1":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 95,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "D#1":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 94,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "E1":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 93,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "F1":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 92,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "F#1":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 91,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "G1":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 90,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "G#1":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 89,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "A1":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 88,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "A#1":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 87,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "B1":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 86,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "C2":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 85,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "C#2":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 84,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "D2":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 83,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "D#2":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 82,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "E2":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 81,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "F2":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 80,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "F#2":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 79,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "G2":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 78,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "G#2":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 77,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "A2":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 76,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "A#2":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 75,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "B2":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 74,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "C3":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 73,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "C#3":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 72,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "D3":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 71,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "D#3":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 70,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "E3":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 69,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "F3":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 68,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "F#3":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 67,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "G3":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 66,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "G#3":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 65,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "A3":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 64,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "A#3":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 63,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "B3":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 62,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "C4":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 61,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "C#4":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 60,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "D4":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 59,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "D#4":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 58,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "E4":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 57,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "F4":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 56,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "F#4":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 55,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "G4":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 54,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "G#4":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 53,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "A4":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 52,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "A#4":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 51,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "B4":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 50,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "C5":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 49,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "C#5":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 48,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "D5":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 47,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "D#5":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 46,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "E5":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 45,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "F5":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 44,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "F#5":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 43,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "G5":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 42,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "G#5":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 41,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "A5":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 40,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "A#5":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 39,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "B5":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 38,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "C6":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 37,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "C#6":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 36,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "D6":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 35,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "D#6":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 34,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "E6":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 33,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "F6":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 32,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "F#6":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 31,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "G6":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 30,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "G#6":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 29,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "A6":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 28,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "A#6":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 27,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "B6":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 26,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "C7":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 25,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "C#7":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 24,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "D7":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 23,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "D#7":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 22,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "E7":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 21,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "F7":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 20,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "F#7":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 19,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "G7":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 18,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "G#7":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 17,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "A7":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 16,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "A#7":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 15,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "B7":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 14,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ],
  "C8":
  [
    {
      "type": "circle",
      "center": [0, -0.5],
      "size": 13,
      "angle": [180, 0],
      "line":
      {
        "color": "ffffff",
        "width": 10
      },
      "fill": False
    }
  ]
}



class Screen(gtk.DrawingArea):
  # Init function
  def __init__(self):
    gtk.DrawingArea.__init__(self)

    self.keys = read_keys()

    self.set_flags(gtk.CAN_FOCUS)

    self.connect("expose-event", self.expose)

    # Init pyportmidi
    pypm.Initialize()
    count = pypm.CountDevices()
    devices = []
    for id in range(count):
      dev = pypm.GetDeviceInfo(id)
      if dev[2]:
        d = list(dev)
        d.append(id)
        devices.append(d)
    if devices:
      print "Choose your MIDI device:"
      for dev in devices:
        print "ID: %d, %s interface is %s"%(dev[5], dev[0], dev[1])
    else:
      print "Sorry, no MIDI input device found. :("
      exit(1)

    dev = int(raw_input("Your choice: "))

    try:
      self.dev = pypm.Input(dev)
    except:
      print "Invalid ID or bad MIDI device."
      exit(1)

    # Timeout for MIDI device
    gobject.timeout_add(0, self.midi_timeout)

    # Timeout for refresh screen
    gobject.timeout_add(0, self.expose_timeout)

  def midi_timeout(self):
    if not self.dev.Poll():
      gobject.timeout_add(10, self.midi_timeout)
      return
    raw = self.dev.Read(1)
    #~while raw:
      #~if raw[0][0][0] == 144:
        #~self.keys[calc_chord(raw[0][0][1])].switch(bool(raw[0][0][2]))
        #~raw = self.dev.read(1)
    if raw[0][0][0] == 144:
      self.keys[calc_chord(raw[0][0][1])].switch(bool(raw[0][0][2]))
    gobject.timeout_add(0, self.midi_timeout)
    return

  def expose_timeout(self):
    self.expose()
    gobject.timeout_add(40, self.expose_timeout)

  # Exposé event handler
  def expose(self, widget=None, event=None):

    cr = self.window.cairo_create()

    cr.rectangle(0, 0, *self.window.get_size())
    cr.set_source_rgba(0.0, 0.0, 0.0, 1.0)
    cr.fill()

    for n in self.keys:
      self.keys[n].draw(cr, *self.window.get_size())


# Main class
class Window(gtk.Window):
  def __init__(self):
    gtk.Window.__init__(self)

    # Flag for indicate fullscreened
    self.fullscreen_flag = False

    # Set some gtk stuff
    self.set_flags(gtk.CAN_FOCUS)
    self.set_events(gtk.gdk.KEY_PRESS_MASK)

    # Set title and icon
    self.set_title("MiDraw - a Dalma Kadocsa and Zsombor Hollay-Horváth coproducion")

    # Set sizes
    self.set_default_size(640, 480)

    # Set handlers
    self.connect("destroy",         self.__destroy)
    self.connect("key-press-event", self.__on_key_press)
    self.connect("realize", self.realize_cb)

    # Set slice
    self.screen = Screen()
    self.add(self.screen)

    # Show and start gtk main loop
    self.show_all()
    gtk.main()

  # 'Are you sure?'
  def __destroy(self, widget, data=None):
    gtk.main_quit()

  # Special keys handler
  def __on_key_press(self, widget, event):
    keyval = gtk.gdk.keyval_name(event.keyval)
    # Fullscreen handler
    if keyval == 'F11':
      if self.fullscreen_flag:
        self.fullscreen_flag = False
        self.unfullscreen()
      else:
        self.fullscreen_flag = True
        self.fullscreen()
      return True
    if keyval == 'F12':
      self.screen.window.cairo_create().get_group_target().write_to_png('screenshots/'+timecode('%Y-%m-%d-%H:%M:%S')+'.png')

  def realize_cb(self, widget):
    pixmap = gtk.gdk.Pixmap(None, 1, 1, 1)
    color = gtk.gdk.Color()
    cursor = gtk.gdk.Cursor(pixmap, pixmap, color, color, 0, 0)
    widget.window.set_cursor(cursor)

try:
  main = Window()
except:
  pass
