import os, sys, time
import bluetooth
import signal
import ConfigParser
from optparse import OptionParser
from bluetooth import BluetoothError

""" 
Bluetooth Device Tracker Daemon 

http://github.com/thiagomoretto

requires bluez and python bluez bindings (PyBluez)
"""

__author__ = "Thiago Moretto"
__copyright__ = "GPL"
__version__ = "0.1"

options=None
__DEF_LOG="/var/log/tracker.log"
if(hasattr(os,"devnull")):
	STDOUT = os.devnull

daemon_pid=0
f=None

def loginfo(type,message):
	if options.verbose:
		f.write("(pid=%d) %s %s: %s\n" % (daemon_pid,time.ctime(time.time()),type,message))
		f.flush()

def sighandler(signum, frame):
	loginfo("INFO","quit")
	f.close()
	os._exit(0); 

signal.signal(signal.SIGTERM,sighandler);

def tracker():
	cache={}
	devices={}
	try:
	    while 1:
		nearby_devices = bluetooth.discover_devices()
		cache={}
		for founded_addr in nearby_devices:
			target_name = bluetooth.lookup_name(founded_addr)
			cache[founded_addr]=target_name
			if founded_addr not in devices:
				devices[founded_addr]=target_name
				handler.entry(target_name,founded_addr)
				loginfo("ENTRY","%s: %s"%(target_name,founded_addr))
		
		for k in devices.keys():
			if k not in cache:
				loginfo("QUIT","%s: %s"%(devices.get(k),k))
				handler.quit(devices.get(k),k)
				del devices[k]
		handler.update(devices)
		loginfo("UPDATE","devices: %s"%devices)
		if options.repeat==False:
			loginfo("INFO","quit")
			break
		time.sleep(options.sleeptime);
	except BluetoothError,e:
		print >>sys.stderr, "error: %s"%e


if __name__ == "__main__":

	sys.path.append("handlers");

	parser = OptionParser(version=__version__)
	parser.add_option("-p","--handler",dest="handler",default="handler", help="use python handler. Metaclass: Handler")
	parser.add_option("-l",dest="logfile", default="/var/log/tracker.log", 
		help="setup log file to append messages")
	parser.add_option("-q",action="store_false",dest="verbose",default=True,help="be quiet, NO LOG")
	parser.add_option("-s","--sleep",action="store",dest="sleeptime",type="int",default=30,
			help="time, in seconds, beetween scans")
	parser.add_option("-o",action="store_false",dest="repeat",default=True,
			help="Don't repeat. Only scan devices one time")

	ready=False
	(options,args) = parser.parse_args()
	if options.logfile:
		__DEF_LOGFILE=options.logfile
	f=open(__DEF_LOGFILE,"a");

	if options.handler:
		try:
			module=options.handler
			if '/' in module:
				module=module.split('/')
				module=module[len(module)-1]
			if module[-3:] == '.py':
				module=module[0:len(module)-3]
			exec "from %s import Handler"%module;
			loginfo("INFO", "Loading handler %s"%module)
			handler=Handler()
			ready=True
		except ImportError,e:
			print >>sys.stderr, "handler import failed with error: %s"%e
		
	try:
		pid = os.fork()
		if pid > 0:
			sys.exit(0)
	except OSError, e:
		print >>sys.stderr, "fork #1 failed with error: %s" % e.strerror

	os.chdir("/");
	os.setsid();
	os.umask(0);

	try:
		daemon_pid = os.fork()
		if daemon_pid > 0:
			os.system("echo %s >/var/run/tracker.pid"%daemon_pid)
			sys.exit(0)
	except OSError, e:
		print >>sys.stderr, "fork #2 failed with error: %s" % e.strerror
		sys.exit(1)

	if ready:
		loginfo("INFO","Tracker ready!")
		tracker()
