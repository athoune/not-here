#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import datetime
import socket

from icalendar import Calendar, Event, vDatetime, vDate

class Server:
	def __init__(self, port= 50007):
		self.HOST = ''                 # Symbolic name meaning the local host
		self.PORT = port              # Arbitrary non-privileged port
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.bind((self.HOST, self.PORT))
		#format of response message(DO NOT ALTER IF YOU DONT KNOW WHAT U R DOING)
		self.calendar = None
	def forever(self):
		self.s.listen(1)
		while 1:
			conn, addr = self.s.accept()
			print 'Connected by', addr
			data = conn.recv(1024)
			if not data: break
			print data
			data ='''HTTP/1.0 200 OK
			Connection: close
			Content-Length: %i
			Content-Type: text/calendar

			%s''' % (len(self.calendar), self.calendar)
			conn.send(data)
			conn.close()	

class MetaCalendar:
	def __init__(self, name):
		self.name = name
		self.cal = Calendar()
	def append(self, event):
		self.cal.add_component(event)
	def __str__(self):
		return self.cal.as_string()
	def store(self):
		f = open('%s.ics' % self.name, 'w')
		f.write(self.cal.as_string())
		f.close()

if __name__ == '__main__':
	vacance = MetaCalendar('vacance')
	cal = Calendar.from_string(open('test.ics','rb').read())
	for component in cal.walk():
		#print component.name, component.keys()
		if component.name == 'VEVENT':
			print component['summary'], component['dtstart'].dt, component['dtend'].dt
			vacance.append(component)
	server = Server()
	server.calendar = str(vacance)
	server.forever()

