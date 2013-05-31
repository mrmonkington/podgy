#!/usr/bin/python
import sys
import time
import memcache

import settings

from podgy import parse, robots, classifier

def main():
    parser = parse.Parser()
    robotest = robots.Bladerunner(settings.ROBOTS_FILE, settings.ROBOTS_FORMAT)
    classy = classifier.Classifier()
    mc = memcache.Client(settings.MEMCACHE_HOSTS, debug=0)
    now = time.time()
    counters = [
        {'start': now, 'key': 'sec', 'period': 1, 'count': 0, 'last': 0 },
        {'start': now, 'key': 'min', 'period': 60, 'count': 0, 'last': 0 },
        {'start': now, 'key': 'hour', 'period': 60*60, 'count': 0, 'last': 0 },
        {'start': now, 'key': 'day', 'period': 24*60*60, 'count': 0, 'last': 0},
    ]

    for ln in sys.stdin:
        try:
            if classy.classify_raw(ln) == "page":
                rec = parser.parse_line(ln)
                if robotest.validate(rec):
                    now = time.time()
                    for counter in counters:
                        if now > counter["start"] + counter["period"]:
                            mc.set("%s/pageviews/%s" % (settings.KEY_PREFIX, counter["key"]), {"time": now, "count": counter["count"]})
                            #print "pageviews/%s" % counter["key"], { "time": now, "count": counter["count"] }
                            counter["start"] = now
                            counter["last"] = counter["count"]
                            counter["count"] = 0
                        counter["count"] += 1 
        except parse.CorruptRecord:
            pass

if __name__ == "__main__":
    main()
    #import cProfile
    #cProfile.run('main()')
