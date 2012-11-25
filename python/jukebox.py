#!/usr/bin/env python
#
import sys, os, random, time, signal
import subprocess
import humble
import threading
from mpd import (MPDClient, CommandError)
from socket import error as SocketError


# MPD Stuff
HOST = 'localhost'
PORT = '6600'
CON_ID = {'host':HOST, 'port':PORT}

PLAYER = "mpc"
PAUSE = 0.2
DISPLAYSLEEP = 5


# Some functions
def mpdConnect(client, con_id):
    """
    Simple wrapper to connect MPD.
    """
    try:
        client.connect(**con_id)
    except SocketError:
        return False
    return True

class DisplayThread(threading.Thread):
  def __init__(self, jb):
    threading.Thread.__init__(self)
    self.jukebox = jb
    self.daemon = True

  def run(self):
    while (True):
        time.sleep(DISPLAYSLEEP)
        status = self.jukebox.client.status()
        print status
        info = self.jukebox.client.currentsong()
        humble.line(0,info['artist'])
        humble.line(1,info['title'])
        if status['state'] == 'pause' or status['state'] == 'stop':
            humble.led('red',True)
            humble.led('green',False)
        else:
            humble.led('red',False)
            humble.led('green',True)

class Jukebox():
  def __init__(self):
    self.dt = DisplayThread(self)
    self.dt.start()

    ## MPD object instance
    self.client = MPDClient()
    if mpdConnect(self.client, CON_ID):
        print 'Got connected!'
    else:
        print 'fail to connect MPD server.'
        sys.exit(1)
    carryOn = True
    while (carryOn):
        if (humble.switch(0)):
            time.sleep(PAUSE)
            self.toggle()
        if (humble.switch(1)):
            time.sleep(PAUSE)
            self.skip()
        if (humble.switch(2)):
            time.sleep(PAUSE)
            self.stop()
            carryOn = False
            time.sleep(PAUSE)

  def skip(self):
      print "Skipping"
      self.client.next()

  def stop(self):
      print "Stopping"
      self.client.stop()
      humble.line(0,"")
      humble.line(1,"")
      humble.led('red', False)
      humble.led('green', False)
      time.sleep(0.5)

  def toggle(self):
      status = self.client.status()
      if status['state'] == 'pause' or status['state'] == 'stop':
          self.client.play()
      else:
          self.client.pause()

def main():
  humble.init()
  time.sleep(0.5)
  jb = Jukebox()

if __name__ == '__main__':
  main()