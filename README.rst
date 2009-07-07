Not here
========

Not here is a simple tool to consolidate holidays from multiple iCal calendars.

A simple text pattern is used to extract specific events.

A basic http server is provided to test with iCal.

Install
-------

depencencies::

  easy_install -U pyyaml icalendar

Try it
------
Copy nothere-default.yml to nothere.yml

Modify the conf file as you wich, multiple calendars are handled

Launch it::

  python nothere.py
  open webcal://localhost:50007/holidays.ics