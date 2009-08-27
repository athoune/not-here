#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

import sys
import datetime
import socket
import glob
import os.path

#http://codespeak.net/icalendar/
from icalendar import Calendar, Event, vDatetime, vDate, vText
import yaml

class Server(object):
	"""
	A crude http server to test import from iCal
	http://code.activestate.com/recipes/576541/
	[TODO] utiliser le serveur compatible wsgi proposé par Python
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
				calendar = self.calendar[what].cal.as_string()
				data ='''HTTP/1.0 200 OK
Connection: close
Content-Length: %i
Content-Type: text/plain

%s''' % (len(calendar), calendar)
			conn.send(data)
			conn.close()	

class MetaCalendar(object):
	"""The calendar object
	"""
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
		self.size = 0
	def append(self, event):
		#pass
		self.cal.add_component(event)
		self.size +=1
	def __str__(self):
		return self.cal.as_string()
	def store(self):
		f = open('%s.ics' % self.name, 'w')
		f.write(self.cal.as_string())
		f.close()
	def __repr__(self):
		return '<Calendar %s #%i>' % (self.name, self.size)

def getSources(path):
	if path.startswith('http://'):
		return
	if path.startswith('https://'):
		return
	for source in glob.glob(path):
		yield open(source, 'rb').read()

class Config(object):
	"""The config object wich read the yaml configurations file
	"""
	def __init__(self, conf = 'nothere.yml'):
		self.conf = yaml.load(open(conf, 'rb').read())
		self.port = self.conf['server']['port']
		self.sources = []
		sources = self.conf['sources']
		if not hasattr('__iter__', sources):
			sources = [sources]
		for source in sources:
			for s in glob.glob(source):
				self.sources.append(s)
		self.calsources = {}
		for source in self.sources:
			self.calsources[source.split('/')[-1]] = Calendar.from_string(open(source,'rb').read())
		self._calendars = None
	def calendars(self):
		"Ready to eat calendars data"
		if self._calendars == None:
			self._calendars = {}
			for calendar in self.conf['calendars']:
				meta = MetaCalendar(calendar['name'], calendar['title'], calendar.get('summary', ''), calendar.get('color', '#0252D4'))
				for user, source in self.calsources.iteritems():
					acronyme = user.split('.')[0]
					for component in source.walk():
						if component.name == 'VEVENT':
							for pattern in calendar['pattern']:
								if component['summary'].lower().find(pattern) == 0:
									print acronyme, component['dtstart'].dt, component['dtend'].dt, component['summary']
									component['summary'] = vText(u"%s ☞ %s" % (acronyme, component['summary']))
									meta.append(component)
									break
				self._calendars[meta.name] = meta
		return self._calendars
	def server(self):
		"Serve calendar with http"
		server = Server()
		for name, calendar in self.calendars().iteritems():
			server[name] = calendar
		server.forever()
if __name__ == '__main__':
	if os.path.exists('nothere.yml'):
		conf = Config('nothere.yml')
		print conf.port
		print conf.sources
		print conf.calendars()
		conf.server()
	else:
		print "I need a conf file named 'nothere.yml"
