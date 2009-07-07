#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import datetime
import socket
import glob

from icalendar import Calendar, Event, vDatetime, vDate
import yaml

class Server(object):
	"""
	http://code.activestate.com/recipes/576541/
	"""
	def __init__(self, port= 50007):
		self.HOST = ''                 # Symbolic name meaning the local host
		self.PORT = port              # Arbitrary non-privileged port
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.bind((self.HOST, self.PORT))
		#format of response message(DO NOT ALTER IF YOU DONT KNOW WHAT U R DOING)
		self.calendar = {}
	def __setitem__(self, key, value):
		self.calendar[key] = value
	def forever(self):
		self.s.listen(1)
		while 1:
			conn, addr = self.s.accept()
			print 'Connected by', addr
			data = conn.recv(1024)
			if not data: break
			what = data.split(' ')[1][1:-4]
			print "url:", what
			if what not in self.calendar:
				data ='''HTTP/1.0 404 NOT FOUND
Connection: close

'''
			else:
				calendar = self.calendar[what]
				data ='''HTTP/1.0 200 OK
Connection: close
Content-Length: %i
Content-Type: text/plain

%s''' % (len(calendar), calendar)
			conn.send(data)
			conn.close()	

class MetaCalendar(object):
	def __init__(self, name, title, summary="", color = '#0252D4', tz = 'Europe/Paris'):
		self.name = name
		self.cal = Calendar()
		self.cal['summary'] = summary
		self.cal['X-APPLE-CALENDAR-COLOR'] = color
		self.cal['X-WR-CALNAME'] = title
		self.cal['calscale'] = 'GREGORIAN'
		self.cal['X-WR-TIMEZONE'] = tz
		self.cal['version'] = '2.0'
		self.cal['method'] = 'PUBLISH'
		self.cal['prodid'] = '-//Garambrogne Inc.//Not here 1.0//FR'
	def append(self, event):
		#pass
		self.cal.add_component(event)
	def __str__(self):
		return self.cal.as_string()
	def store(self):
		f = open('%s.ics' % self.name, 'w')
		f.write(self.cal.as_string())
		f.close()
	def __repr__(self):
		return '<Calendar %s>' % self.name

class Conf(object):
	def __init__(self, conf = 'nothere.yml'):
		self.conf = yaml.load(open(conf, 'rb').read())
		self.port = self.conf['server']['port']
		self.sources = []
		sources = self.conf['sources']
		if hasattr('__iter__', sources):
			for source in sources:
				for s in glob.glob(source):
					self.sources.append(s)
		else:
			for s in glob.glob(sources):
				self.sources.append(s)
		self.calsources = {}
		for source in self.sources:
			self.calsources[source.split('/')[-1]] = Calendar.from_string(open(source,'rb').read())
		self._calendars = None
	def calendars(self):
		if self._calendars == None:
			self._calendars = {}
			for calendar in self.conf['calendars']:
				meta = MetaCalendar(calendar['name'], calendar['title'], calendar.get('summary', ''), calendar.get('color', '#0252D4'))
				for user, source in self.calsources.iteritems():
					for component in source.walk():
						if component.name == 'VEVENT':
							for pattern in calendar['pattern']:
								if component['summary'].lower().find(pattern):
									meta.append(component)
									continue
				self._calendars[meta.name] = meta
		return self._calendars
if __name__ == '__main__':
	conf = Conf('nothere.yml')
	print conf.port
	print conf.sources
	print conf.calendars()
	if len(sys.argv) == 1:
		calendars = ['test.ics']
	else:
		calendars = sys.argv[1:]
	"""
	vacance = MetaCalendar('vacances')
	for calendar in calendars:
		cal = Calendar.from_string(open(calendar,'rb').read())
		for component in cal.walk():
			#print component.name, component.keys()
			if component.name == 'VEVENT':
				print component['summary'], component['dtstart'].dt, component['dtend'].dt
				vacance.append(component)
	vacance.store()
	"""
	#server = Server()
	#server['vacances'] = str(vacance)
	#server.forever()

