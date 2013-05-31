import sys
import re
import Ft.Xml.Domlette

# global config store
podge = False

class Error( Exception ):
	pass
class ParseError( Error ):
	pass

class PodgeConf( object ):

	# inactivity required for a client to be considered a new session
	SESSION_TIMEOUT = 10
	
	def __init__( self, conf_file ):
		self.robots = []
		self.reports = []
		self.trackers = []
		try:
			xdom = Ft.Xml.Domlette.NonvalidatingReader.parseStream( open( conf_file ), conf_file )
			# setup globals
			xglobals = xdom.xpath( u"podge/globals" )[ 0 ]
			self.SESSION_TIMEOUT = int( xglobals.xpath( u"string( session-timeout )" ) )

			# exclusion list
			xrobots = xdom.xpath( u"podge/exclusions/import[ @type = 'robot' ]" )
			for rob in xrobots:
				self.robots.append( {
					"src" : rob.attributes[ ( None, u"src" )].value,
					"format" : rob.attributes[ ( None, u"format" )].value
				} )

			# reports
			xreports = xdom.xpath( u"podge/report" )
			for xrep in xreports:
				label = xrep.attributes[ ( None, u"label" ) ].value
				self.reports.append( {
					"label" : label
				} )
				xtrackers = xrep.xpath( u"tracker" )
				for xt in xtrackers:
					track = {
						"report" : label,
						"label" : xt.attributes[ ( None, u"label" ) ].value,
						"uri" : self.convert_xmelly_braces( xt.attributes[ ( None, u"uri" ) ].value ),
						"impressions" : self.attr_default( xt, u"impressions", self.cast_bool, False ),
						"visits" : self.attr_default( xt, u"visits", self.cast_bool, False ),
						"uniques" : self.attr_default( xt, u"uniques", self.cast_bool, False ),
					}
					self.trackers.append( track )

		except Ft.FtException, e:
			raise ParseError( e )

	def convert_xmelly_braces( self, s ):
		"""
		XML attributes can't contain naked < and > so we let users use { } for named
		groups in regexps and convert them after reading
		"""

		return re.sub(  r"\(\?P\{([a-zA-Z0-9_]+)\}", r"(?P<\1>", s )
	
	def cast_bool( self, val ):
		if val.upper() == "TRUE":
			return True
		return False

	def attr_default( self, node, attrname, cast, default ):
		if node.attributes.has_key( ( None, attrname ) ):
			return cast( node.attributes[ ( None, attrname ) ].value )
		else:
			return default

if __name__ == "__main__":
	p = PodgeConf( sys.argv[ 1 ] )
	print p.trackers

