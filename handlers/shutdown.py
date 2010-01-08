import os, sys
from handler import *

"""
Shutdown Handler
"""
device="00:0E:6D:89:E8:91"

class Handler:
   __metaclass__ = Handler
   def entry(self,name,addr): pass
   def update(self,devices): pass
   def quit(self,name,addr):
	if addr==device:
		os.system("poweroff")



