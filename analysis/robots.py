import sys
import re

class UnsupportedFormatError( Exception ):
	pass

class Bladerunner:
	"""
	Kills robots
	"""

	robots = []

	def __init__( self, src, format ):
		# load robot definition
		if format == "abce":
			for ln in open( src ):
				ln = ln.strip()
				if ln[ 0 ] == "#" or ln == "":
					continue
				( pattern, active, exceptions, twopass_redundant, target, expiry ) = ln.split( "|" )
				if active == "1":
					# TODO check the abce robots don't need regexp quoting
					self.robots.append( {
						"pattern" : re.compile( re.escape( pattern ), re.I ),
						"exceptions" : re.compile( exceptions.replace( ",", "|" ) )
					} )
		else:
			raise UnsupportedFormatError( format )

	def validate( self, match ):
		for robot in self.robots:
			# TODO check robot exceptions list
			if robot[ "pattern" ].search( match[ "client_useragent" ] ):
				return False
		return True

if __name__ == "__main__":
	r = Bladerunner( "doc/abce_exclude_20090128.txt", "abce" )
	v = r.validate( { "client_useragent" : "apachebench" } )
	print v
	v = r.validate( { "client_useragent" : "the apachebench" } )
	print v
	v = r.validate( { "client_useragent" : "the apachebench v2" } )
	print v
	v = r.validate( { "client_useragent" : "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.3) Gecko/2008092510 Ubuntu/8.04 (hardy) Firefox/3.0.3" } )
	print v
