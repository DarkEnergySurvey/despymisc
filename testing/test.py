#!/usr/bin/env python

"""
A simple method to compare the old vs new method to compute nite.
F. Menanteau Nov, 2015
"""

###########################################
# Functions for testing against old method 
def parse_json(filename):
    import json
    dates = []
    with open(filename) as data_file:    
        data = json.load(data_file)
        
    dates = [item['date'] for item in data["exposures"]]
    dates.append(data['header']['createdAt'])
    return dates

def read_json(pattern):
    import glob
    files = glob.glob(pattern)
    all_dates = []
    for file in files:
        #print "Reading %s" % file
        all_dates = all_dates + parse_json(file)
    return all_dates

######################################################################
def convert_utc_str_to_nite_old(datestr):
    import pytz
    import datetime
    from dateutil.parser import parse
    from dateutil import tz

    """ Convert an UTC date string to a nite string """

    # e.g. datestr: 2014-08-15T17:31:02.416533+00:00
    nite = None

    # convert date string to datetime object
    utc_dt = parse(datestr)

    # convert utc to local on mountain
    local_tz = pytz.timezone('Chile/Continental') # use your local timezone name here
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    local_dt = local_tz.normalize(local_dt) # .normalize might be unnecessary

    # see if before or after noon on mountain
    noon_dt = local_dt.replace(hour=12, minute=0, second=0, microsecond=0)
    if local_dt < noon_dt:  # if before noon, observing nite has previous date
        obsdate = (local_dt - datetime.timedelta(days=1)).date()
    else:
        obsdate = local_dt.date()

    nite = obsdate.strftime('%Y%m%d')
    return nite


if __name__ == '__main__':

    from despymisc import misctime

    # Testing old vs new code for many objects
    pattern = "/archive_data/desarchive/DTS/snmanifest/*/*.json"
    print "# Will read SN Manifest times from: %s" % pattern
    times = read_json(pattern)
    
    allequal = True
    print "# Will compare NITES for %s dates" % len(times)
    for date in times:
   
        date_old = convert_utc_str_to_nite_old(date)
        date_new = misctime.convert_utc_str_to_nite(date)

        print date_new, date_old
        
        if date_new != date_old:
            allequal = False
            print "# ERROR for %s" % date
            print "A: %s" % date_new
            print "B: %s" % date_old
            print "-----"
    if allequal:
        print "All %s dates are consistent." % len(times)
