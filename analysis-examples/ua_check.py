#!/usr/bin/python
import sys

from podgy import parse, robots, classifier, time

from operator import itemgetter

parser = parse.Parser()
robotest = robots.Bladerunner( "/usr/www/stats/podgy/doc/exclude_current.txt", "abce" )
classifier = classifier.Classifier()
robc = 0
tot = 0
days = {}
uas = {}
for ln in sys.stdin:
    rec = parser.parse_line( ln )
    if classifier.classify( rec ) == "page":

        # track traffic for each day
        day = parse.parsetime( rec )[ "req_datetime_struct" ][ 2 ]
        if not days.has_key( day ):
            days[ day ] = 0
        days[ day ] += 1
        if not uas.has_key( rec["client_useragent"] ):
            uas[rec["client_useragent"]] = 0
        uas[rec["client_useragent"]] += 1
        tot += 1
        if not robotest.validate( rec ):
            robc += 1

print "Total of %i pages of which %i were robots" % (tot, robc)
print days
for ( ua, c ) in  sorted( uas.iteritems(), key=itemgetter(1) ):
    print c, ua
