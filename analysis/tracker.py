import sys
import re
import config
import hashlib

"""
Podgy Tracker

Configuration contains a uri pattern that is applied to the TREATED url
and can specify breakout variables

eg:
url: ^http://www.eurogamer.net/articles/(?P<article_name>[::path-chunk::])

we define some match classes like url-chunk (or wotever) for readability
this will create a unique entry for each URL that has a unique article, but
will ignore subsequent queries

eg
url: ^http://www.eurogamer.(?P<eg_locale>[::domain-chunk::])/articles/[::path-chunk::].*[::query-delimiter::]page=(?P<page_num>[::integer::]+)

this will match all articles but will aggregate the count for all views with same pagenumber
which could be quite useful

patterns recorded in DB only substitute the named matches, leaving non-named patterns
intact

eg: http://www.eurogamer.net/articles/[::path-chunk::].*[::query-delimeter::]page=2

"""
# mnemonics for common patterns
chunks = {
	"integer" : r"[0-9]+",
	"domain" : r"[a-zA-Z\.\-0-9]+",
	"domain-chunk" : r"[a-zA-Z\-0-9]+",
	"path-chunk" : r"[^\&\?/]+",
	"path" : r"[^\?\&]+/",
	"query-delimiter" : r"[\?\&]"
}

# TODO
# make query string matching order independent -- otherwise developers have to
# be very organised when site building, which just ain't gonna happen!

# TODO
# allow translation of variables into a more readable/meaningful form
# e.g. article=23453254 -> article-name

# TOCONSIDER
# allow labelling of untracked matches
# e.g. www.eurogamer.[``[::domain-chunk::]`any TLD``]

class Tracker( object ):

	# decl: pattern = r".*"
	# decl: tokens
	# decl: template
	# decl: human_pattern

	def __init__( self, pattern ):
		self.human_pattern = pattern
		self.pattern = pattern
		self.activity = {}
		for c in chunks.keys():
			self.pattern = re.sub( r"\[\:\:" + c + r"\:\:\]", chunks[ c ], self.pattern )

		# bit of a brain masher and probably won't find a use for this list
		self.tokens = re.findall( r"\(\?P\<([a-zA-Z0-9_\-]+)\>[^\)]+\)", self.pattern )
		# if we get a match on a req we want a template for inserting named vars into
		self.template = re.sub( r"\(\?P\<([a-zA-Z0-9_\-]+)\>[^\)]+\)", r"\\g<\1>", self.human_pattern )
		# for efficiency compile pattern
		self.reg = re.compile( self.pattern )

	def match( self, record ):
		m = self.reg.search( record[ "req_uri" ] )
		if m:
			breakout = m.expand( self.template )
			return ( True, breakout )
		return ( False, None )
	
	def track( self, record ):
		( m, breakout ) = self.match( record )
		if m:
			if not self.activity.has_key( breakout ):
				self.activity[ breakout ] = ActivityWindow()
			if self.activity[ breakout ].start == 0:
				self.activity[ breakout ].start = record[ "req_timestamp" ]

			id = self.make_session_id( record[ "client_ip" ], record[ "client_useragent" ] )
			#print >>sys.stderr, id

			if not self.activity[ breakout ].clients.has_key( id ):
				#print >>sys.stderr, "New visitor: " + id
				self.activity[ breakout ].clients[ id ] = Client(
					{
						"ip" : record[ "client_ip" ],
						"useragent" : record[ "client_useragent" ]
					},
					record[ "req_timestamp" ]
				)

			self.activity[ breakout ].clients[ id ].hit_current_session( record )

	def make_session_id( self, ip, ua ):
		return "%s/%s" % ( ip, hashlib.md5( ua ).digest() )
		#return "%s/%s" % ( ip, ua )

class ClientSession:
	def __init__( self ):
		self.impressions = []
		self.last_seen = 0
		self.start = 0


class Client:
	# profile is a list of values that can be combined to form this
	# session's index in sesh list

	# decl: profile = {
	#	"ip" : "",
	#	"user_agent" : ""
	#}
	# decl: sessions 
	# decl: current_session

	def __init__( self, profile, ts ):
		self.profile = profile
		self.sessions = []
		self.current_session = 0
		self.new_session( ts )
		# TODO
		# DB: insert into clients

	def new_session( self, ts ):
		self.sessions.append( ClientSession() )
		self.current_session = len( self.sessions ) - 1
		self.sessions[ self.current_session ].start = ts
		self.sessions[ self.current_session ].last_seen = ts

	def get_session( self, ts ):
		if self.sessions[ self.current_session ].last_seen < ( ts - config.podge.SESSION_TIMEOUT ):
			self.new_session( ts )
		
		return self.sessions[ self.current_session ]

	def hit_current_session( self, record ):
		#print >>sys.stderr, "hit"
		session = self.get_session( record[ "req_timestamp" ] )
		session.impressions.append( record )
		session.last_seen = record[ "req_timestamp" ]

		# TODO
		# DB: insert into url_client_session

class ActivityWindow:

	# decl: start = 0
	# decl: end = 0

	# dict of client sessinos indexed by client unique profile id (ip + ua, for instance)
	# decl: clients 

	def __init__( self ):
		self.clients = {}
		self.start = 0
		self.end = 0
	

if __name__ == "__main__":
	#t = Tracker( r"^http://www.eurogamer.net/articles/(?P<article_name>[::path-chunk::])" )
	#print t.pattern
	#print t.template
	t = Tracker( r"^http://www.eurogamer.(?P<eg_locale>[::domain-chunk::])/articles/[::path-chunk::].*[::query-delimiter::]page=(?P<page_num>[::integer::])" )
	print t.pattern
	print t.template
	print t.match( { "req_uri" : "http://www.eurogamer.net/articles/monkey-ball-2-review?page=2" } )
