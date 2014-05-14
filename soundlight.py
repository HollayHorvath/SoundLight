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

import pyportmidi

import json


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
  try:
    raw = open("keys.dat").readlines()
  except:
    print "Cannot open file keys.dat. Abort."
    exit(1)
  dat = ""
  for i in raw:
    dat+=i.strip()

  obj = json.loads(dat)

  for i in obj:
    obj[i] = note(obj[i])

  return obj


class Screen(gtk.DrawingArea):
  # Init function
  def __init__(self):
    gtk.DrawingArea.__init__(self)

    self.keys = read_keys()

    self.set_flags(gtk.CAN_FOCUS)

    self.connect("expose-event", self.expose)

    # Init pyportmidi
    pyportmidi.init()
    count = pyportmidi.get_count()
    devices = []
    for id in range(count):
      dev = pyportmidi.get_device_info(id)
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
      self.dev = pyportmidi.Input(dev)
    except:
      print "Invalid ID or bad MIDI device."
      exit(1)

    # Timeout for MIDI device
    gobject.timeout_add(0, self.midi_timeout)

    # Timeout for refresh screen
    gobject.timeout_add(0, self.expose_timeout)

  def midi_timeout(self):
    if not self.dev.poll():
      gobject.timeout_add(10, self.midi_timeout)
      return
    raw = self.dev.read(1)
    #~while raw:
      #~if raw[0][0][0] == 144:
        #~self.keys[calc_chord(raw[0][0][1])].switch(bool(raw[0][0][2]))
        #~raw = self.dev.read(1)
    if raw[0][0][0] == 144:
      self.keys[calc_chord(raw[0][0][1])].switch(bool(raw[0][0][2]))
      raw = self.dev.read(1)
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
