# -*- coding: utf-8 -*-
"""
Created on Sun Jun 26 15:37:23 2011

@author: btaratutin
"""

import sys

### TO disable printing, call


class dummyStream:
	''' dummyStream behaves like a stream but does nothing. '''
	def __init__(self): pass
	def write(self,data): pass
	def read(self,data): pass
	def flush(self): pass
	def close(self): pass

# Copy old print deals
old_printerators=[sys.stdout,sys.stderr,sys.stdin,sys.__stdout__,sys.__stderr__,sys.__stdin__][:]
# redirect all print deals
sys.stdout,sys.stderr,sys.stdin,sys.__stdout__,sys.__stderr__,sys.__stdin__=dummyStream(),dummyStream(),dummyStream(),dummyStream(),dummyStream(),dummyStream()


# Call your code (not) to print here
print "suppressed hello"


#Turn printing back on!
sys.stdout,sys.stderr,sys.stdin,sys.__stdout__,sys.__stderr__,sys.__stdin__=old_printerators

print "actual hello"