# -*- coding: utf-8 -*-
"""

A logger script that allows you to easily write messages to a text log.
Don't worry about the saving - the program takes care of everything

Created on Wed Jun 29 21:22:29 2011

@author: btaratutin
"""
import datetime
import os

class Log:

    def __init__(self):
        
        # Figure out current time for filename
        now = datetime.datetime.now()
        now_s = "%d.%d.%d - %dh.%dm.%ds" % (now.month, now.day, now.year, now.hour, now.minute, now.second)
        
        # Name file
        #onedirup = os.path.split(os.getcwd())[0]
        self.name = "%s\\Log\\Log - %s.txt" % (os.getcwd(), now_s)
        
        # Create Log File
        self.log = file(self.name, 'w')
        self.log.close()
    
    
    def write(self, s):
        """ Adds the string to the log as a new line """
        
        # Read the contents of the old log & append new string to it
        self.log = file(self.name, 'r')
        file_contents = self.log.read()
        file_contents += "%s\n" % s
        #TODO: unicode decode error. Can't decode ASCII letter
        # ..?
        
        # Close the old log and write the new contents to it
        self.log.close()
        self.log = file(self.name, 'w')
        self.log.write(file_contents)
        
        # Close (save) at the end so we're always in good stature
        self.log.close()
        
        
if __name__ == "__main__":
    l = Log()
    l.write("hello")
    l.write("poop!")
    