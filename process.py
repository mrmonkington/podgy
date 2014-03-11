import sys
import re
import optparse

# this package
from analysis import parse, robots, classifier, tracker, config 

import pprint
import operator

import time

# global podgy config
#podge = False


class Error( Exception ):
	pass
class ConfigError( Error ):
	pass

class Processor( object ):

	# input stream for log
	input = False

	# optional filtered output stream -- can be used for dumping
	# sanitised logs to an auditable form
	output = False

	# we need to track activity during various windows
	# and fold them together later depending on report request
	# this is a list of levels?
	activity = {
	}

	current_activity = False

	
	def process( self, file ):
 
		p = parse.Parser()
		v = robots.Bladerunner( config.podge.robots[ 0 ][ "src" ], config.podge.robots[ 0 ][ "format" ] )
		c = classifier.Classifier()

		cc = 0
		ll = 0
		last = time.clock()
		for ln in file:
			r = p.parse_line( ln )
			if v.validate( r ):
				ll += 1
				r[ "classification" ] = c.classify( r )
				self.handle_record( r )
			cc += 1
			if cc % 1000 == 0:
				print >>sys.stderr, "  Dumping after %i lines (%i valid = %i%%)" % ( cc, ll, ( 100 * ll / cc ) )
				now = time.clock()
				print >>sys.stderr, "  |  (Current rate: %d lines/sec)" % ( 1000 / ( now - last ) )
				last = now
				self.debug_report()

		self.debug_report()
		
	def debug_report( self ):

		for t in self.trackers:
			print >>sys.stderr, "  +- Tracker: %s" % t.human_pattern
			for breakout in t.activity.keys():
				print >>sys.stderr, "     +- Breakout: %s" % breakout
				if len( t.activity[ breakout ].clients ):
					print >>sys.stderr, "     +- Unique visitors: %i" % len( t.activity[ breakout ].clients )
					visits = reduce(
						operator.add,
						[
							len( t.activity[ breakout ].clients[ id ].sessions )
							for id in t.activity[ breakout ].clients.keys()
						]
					)
					print >>sys.stderr, "     +- Visits: %i" % visits

			#for id in self.current_activity.clients.keys():
			#	print "%d" % ( len( self.current_activity.clients[ id ].sessions ) )
	

	def handle_record( self, record ):
		"""
		Dispatch valid log records to trackers and any other processing bits
		we want to do
		"""
		#print >>sys.stderr, record[ "classification" ]
		if record[ "classification" ] == "page":
			for t in self.trackers:
				t.track( record )


	def run( self ):
		"""
		Initiates log parsing after constructing a load of pattern trackers
		"""

		self.trackers = []
		rep_filt = re.compile( self.options.reports )
		for t in config.podge.trackers:
			if rep_filt.search( t[ "report" ] ):
				print >>sys.stderr, "Tracking %s / %s" % ( t[ "report" ], t[ "label" ] )
				self.trackers.append( tracker.Tracker( t[ "uri" ] ) )

		if len( self.trackers ) < 1:
			raise ConfigError( "No reports match input filter!" )

		self.process( self.input )


	def __init__( self, args ):

		object.__init__( self )
		self.read_args( args )
		config.podge = config.PodgeConf( self.options.configfile )


	def read_args( self, args ):

		parser = optparse.OptionParser(
			usage = "usage: %prog [options]",
			version = "%prog 0.1",
			description = "A web server log analyser."
		)

		parser.add_option(
			"-c",
			"--configfile",
			action = "store",
			type = "string",
			dest = "configfile",
			help = "specify an alternate config FILE [default: %default]",
			default = "config/podgy.conf",
			metavar = "FILE"
		)

		parser.add_option(
			"-r",
			"--reports",
			action = "store",
			type = "string",
			dest = "reports",
			help = "specify which reports to show (regexp) [default: .*]",
			default = ".*"
		)

		#parser.add_option(
		#	"-W",
		#	"--width",
		#	action = "store",
		#	type = "int",
		#	dest = "width",
		#	help = "player canvas width [default: %default]",
		#	default = "640"
		#)

		( self.options, parsed_args ) = parser.parse_args( args )
		if len( parsed_args ) >= 1:
			if parsed_args[ 1 ] == "-":
				print >>sys.stderr, "reading log from stdin"
				self.input = sys.stdin
			else:
				self.input = open( parsed_args[ 1 ] )

		if self.options.reports != ".*" and re.compile( self.options.reports ):
			print >>sys.stderr, "Only tracking reports matching '%s'" % self.options.reports
		#self.input = o


if __name__ == "__main__":
	p = Processor( sys.argv )
	p.run()
