Not here
========

Not here is a simple tool to consolidate holidays from multiple iCal calendars.

A simple text pattern is used to extract specific events.

A basic http server is provided to test with iCal.

ics files are standard, it should works with any software like Sunbird_, iCal or even the mythical Chandler_

In a basic usage, users shares calendars with a webdav sharing, and use a convention for typing events. For example, you should describe your holidays with "holiday: ".
A cron or a watcher build the consolidated calendar when something happens.
In the consolidated calendar, events are prefixed with the file name wich the events came from.

Install
-------

depencencies::

  easy_install -U pyyaml icalendar

Try it
------
Copy nothere-default.yml to nothere.yml

Modify the conf file as you wich, multiple calendars are handled

Launch it::

  ./nothere --server
  open webcal://localhost:50007/holidays.ics
  
.. _Sunbird: http://www.mozilla.org/projects/calendar/
.. _Chandler: http://chandlerproject.org/