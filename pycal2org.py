import sys
import os
import datetime
import argparse
from string import Template

import icalendar
from dateutil import rrule, tz


def is_date(dt):
    """A date is both an instance of date and datetime, so we need this extra
    logic to tell the difference.

    """
    return isinstance(dt, datetime.date) and not isinstance(dt, datetime.datetime)

def is_datetime(dt):
    return isinstance(dt, datetime.datetime)

def datetime_format(dt):
    if is_datetime(dt):
        return '%Y-%m-%d %a %H:%M'
    elif is_date(dt):
        return '%Y-%m-%d %a'
    else:
        raise ValueError('Expected datetime or date object')


class Converter(object):

    OPTIONAL_EVENT_FIELDS = ('summary', 'description', 'location',
                             'categories', 'organizer', 'status',
                             'transp', 'url')

    def __init__(self, args):
        self.args = args

    def read_template(self):
        # Look for template in the current dir first, then in the same
        # directory as the program.
        program_dir = os.path.dirname(sys.argv[0])
        try:
            f = open(self.args.template, 'r')
        except IOError:
            f = open(os.path.join(program_dir, self.args.template), 'r')
        with f:
            template = Template(f.read())
        return template

    def tz_localize(self, dt):
        """Convert a datetime object to the local timezone.  This is not as
        obvious as it seems: the given datetime may have a different DST
        offset compared with the current time.

        For convenience, date objects are returned unchanged.

        """
        if is_datetime(dt):
            return dt.astimezone(self.args.tz)
        elif is_date(dt):
            return dt
        else:
            raise ValueError('Expected datetime or date object')

    def format_dateinterval(self, dtstart, dtend=None):
        dtstart_str = dtstart.strftime(datetime_format(dtstart))
        if dtend == None:
            return '<{}>'.format(dtstart_str)
        dtend_str = dtend.strftime(datetime_format(dtend))
        # If start and stop datetimes belong to the same day, use the more
        # lightweight syntax (org-mode seems to display these more nicely in
        # the calendar view).
        if is_datetime(dtstart) and is_datetime(dtend) and \
           dtstart.date() == dtend.date():
            return '<{}-{}>'.format(dtstart_str,
                                    dtend.strftime('%H:%M'))
        # If both start and stop dates are identical, don't display them as a
        # range.
        elif is_date(dtstart) and is_date(dtend) and \
             dtstart == dtend:
            return '<{}>'.format(dtstart_str)
        else:
            return '<{}>--<{}>'.format(dtstart_str,
                                       dtend_str)

    def generate_dates(self, event):
        """Given an event, generate a list of dates or date intervals (as string)
        suitable for use with org-mode.

        """
        dates = []
        dtstart = self.tz_localize(event['dtstart'].dt)
        if 'dtend' in event:
            dtend = self.tz_localize(event['dtend'].dt)
            # DTEND is exclusive, so the real ending date is one day before
            if is_date(dtend):
                dtend -= datetime.timedelta(days=1)
        else:
            dtend = None
        # Normal case: no repetition
        if not 'rrule' in event:
            dates.append(self.format_dateinterval(dtstart, dtend))
        # Handle recurrent events
        else:
            ruleset = rrule.rruleset()
            rule = rrule.rrulestr(event['rrule'].to_ical().decode('utf-8'),
                                  dtstart=dtstart)
            ruleset.rrule(rule)
            # Parse all types of recurrence constraints
            for prop in ['rdate', 'exdate']:
                if not prop in event:
                    continue
                # This can return either a single value or a list, so it's
                # a mess...
                prop_dates = event[prop]
                if not isinstance(prop_dates, list):
                    prop_dates = [prop_dates]
                for prop_date in prop_dates:
                    # This is a vDDDLists
                    for vddd in prop_date.dts:
                        dt = self.tz_localize(vddd.dt)
                        ruleset.__getattribute__(prop)(dt)
            # We now have a ruleset that expands to a list of starting
            # date or datetime, one for each repetition.
            for dtstart_repeat in ruleset:
                # Compute matching dtend if applicable
                if dtend == None:
                    dtend_repeat = None
                else:
                    dtend_repeat = dtend + (dtstart_repeat - dtstart)
                dates.append(self.format_dateinterval(dtstart_repeat, dtend_repeat))
        return dates

    def generate_org_fragment(self, event):
        template = self.read_template()
        data = {
            'dates': '\n  '.join(self.generate_dates(event)),
        }
        # Optional fields
        for field in self.OPTIONAL_EVENT_FIELDS:
            if field in event:
                data[field] = event[field]
            else:
                data[field] = ""
        # Add a space in front of each line of the description, to avoid
        # stars (*) being interpreted as headlines by org-mode.
        data['description'] = data['description'].replace('\n', '\n ')
        return template.substitute(data)

    def print_ical(self):
        with open(self.args.input_file, 'r') as f:
            cal = icalendar.Calendar.from_ical(f.read())
        for event in cal.walk('vevent'):
            print(self.generate_org_fragment(event))

def timezone(s):
    timezone = tz.gettz(s)
    if timezone == None:
        msg = "'{}' is not a valid timezone".format(s)
        raise argparse.ArgumentTypeError(msg)
    return timezone


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Input ICS file to convert")
    parser.add_argument("--tz", type=timezone, default=tz.tzlocal(),
                        help="Timezone to convert to, for instance "
                        "'Europe/Paris' (default: system timezone)")
    parser.add_argument("--template", default="template.org",
                        help="Org-mode template to use for each event "
                        "(default: '%(default)s')")
    args = parser.parse_args()
    c = Converter(args)
    c.print_ical()
