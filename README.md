# pycal2org

This python script takes an .ics file as input, and generates an org-mode file
containing the events.  Each event is presented in its own section, and date/time
of events are also exported.  Thus, the output is suitable for use with the
org-mode calendar.

It also supports recurring events, with proper handling of excluded dates and
so on (using the excellent `dateutil.rrule` library).

Note that, by default, all times are converted to the local (system) timezone,
because org-mode has no support for specifying the timezone.  You can override
the output timezone using the --tz option.

## Install

pycal2org should support both Python3 (tested) and Python2 (untested).

It needs `dateutil` and `icalendar` as dependencies, you can install them using your
package manager, or just install them locally:

    pip3 install --user -r requirements.txt

## Importing calendars from an URL

A simple shell script is provided to download an ICS file from an URL and convert
it to an org-mode file.  For instance:

    ./import-ics.sh 'https://team.inria.fr/polaris/feed/my-calendar-ics?nmonth=12' ~/org/events/seminars.org

It also supports HTTP authentication by passing an username as third argument.
In this case the script will interactively prompt for the password.  For instance:

    ./import-ics.sh 'https://my-private-calendar.foo.bar' ~/org/events/private.org myusername

In these examples, all output org-mode files are stored in `~/org/events/'`.  To tell
org-mode to load all files from this directory, add this to your `.emacs`:

    (setq org-agenda-files (list "~/org/events/")

A nice way of updating public calendars regularly is of course to use a cron job:

    0,15,30,45 * * * * ~/import-ics.sh 'https://team.inria.fr/polaris/feed/my-calendar-ics?nmonth=12' ~/org/events/seminars.org > /dev/null

## Comparison with other ics to org-mode converters

- [ical2org.awk](http://orgmode.org/worg/code/awk/ical2org.awk): parsing is not
  robust (based on regexp...).  In particular, it completely fails for recurring
  events.

## TODO list

- figure out how to tell emacs to reload org files that have changed.
- when fetching a remote ics source, merge it with the previous fetch
  (so that if some events have been removed in the remote source, we
  still have them locally)

