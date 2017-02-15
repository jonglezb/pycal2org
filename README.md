# pycal2org

This python script takes an .ics file as input, and generates an org-mode file
containing the events.  Each event is presented in its own section, and date/time
of events are also exported.  Thus, the output is suitable for use with the
org-mode calendar

It also supports recurring events, with proper handling of excluded dates and
so on (using the excellent dateutil.rrule library).

Note that, by default, all times are converted to the local (system) timezone,
because org-mode has no support for specifying the timezone.  You can override
the output timezone using the --tz option.

## Install

pycal2org should support both Python3 (tested) and Python2 (untested).

It needs `dateutil` and `icalendar` as dependencies, you can install them using your
package manager, or just install them locally:

    pip3 install --user -r requirements.txt

## Comparison with other ics to org-mode converters

- [ical2org.awk](http://orgmode.org/worg/code/awk/ical2org.awk): parsing is not
  robust (based on regexp...).  In particular, it completely fails for recurring
  events.

## TODO list

- add more metadata to the output (event location, etc)
- when fetching a remote ics source, merge it with the previous fetch
  (so that if some events have been removed in the remote source, we
  still have them locally)

