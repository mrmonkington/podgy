#!/usr/bin/python
import sys

from podgy import parse, robots, classifier, time, memcache

def main():
    parser = parse.Parser()
    robotest = robots.Bladerunner( "/usr/www/stats/podgy/doc/exclude_current.txt", "abce" )
    classy = classifier.Classifier()
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    now = time.time()

    for ln in sys.stdin:
        try:
            if classy.classify_raw( ln ) == "page":
                rec = parser.parse_line( ln )
                if robotest.validate( rec ):
                    now = time.time()
                    for counter in counters:
                        if now > counter["start"] + counter["period"]:
                            mc.set("pageviews/%s" % counter["key"], { "time": now, "count": counter["count"] } )
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
