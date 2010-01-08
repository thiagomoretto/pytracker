import os, sys
from handler import *

"""
Gaim Status Handler
"""

device="00:0E:6D:89:E8:91"

class Handler:
   __metaclass__ = Handler
   def entry(self,name,addr):
	if addr==device: 
		os.system("su thiago -c 'gaim-remote setstatus?status=available'")
   def update(self,devices): pass
   def quit(self,name,addr):
	if addr==device: 
		os.system("su thiago -c 'gaim-remote setstatus?status=away'")


