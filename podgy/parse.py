import sys
import re
import time
import shlex

# this is our default EG/combined varnish log format
# - it's basically combined + a few fields prepended by syslog
# request contains full vhost
defaultreg = """
# syslog's fields
    (?P<sys_month>\S+)
    \s+(?P<sys_day>\S+)
    \s+(?P<sys_time>\S+)
# which server from cluster
    \s+(?P<server_ip>\S+)
# user info
    \s+(?P<client_ip>\S+)
    \s+\-
# for future use
# TODO: have eg session cookie val inserted here
    \s+(?P<client_sesion>\S+)
    \s+\[(?P<req_datetime>\S+/\S+/\S+:\S+:\S+:\S+)
    \s+(?P<req_tz>\S+)\]
    \s+"(?P<req_method>\S+)\s(?P<req_uri>\S+)\s(?P<http_version>\S+)"
    \s+(?P<res_code>\S+)\s+(?P<res_bytes>\S+)
# referrer can contain spaces
    \s+"(?P<ref_uri>[^"]*)"
# user agent can really be absolutely anything
# TODO: see if it can legally contain escaped quotes
    \s+"(?P<client_useragent>[^"]+)"
"""
defaultreg = r'(?P<sys_month>\S+)\s+(?P<sys_day>\S+)\s+(?P<sys_time>\S+)\s+(?P<server_ip>\S+)\s+(?P<client_ip>\S+)\s+\-\s+(?P<client_sesion>\S+)\s+\[(?P<req_datetime>\S+/\S+/\S+:\S+:\S+:\S+)\s+(?P<req_tz>\S+)\]\s+"(?P<req_method>\S+)\s(?P<req_uri>\S+)\s(?P<http_version>\S+)"\s+(?P<res_code>\S+)\s+(?P<res_bytes>\S+)\s+"(?P<ref_uri>[^"]*)"\s+"(?P<client_useragent>[^"]+)"' 
defaultreg = """
    (?P<sys_month>\S+)
    \s+(?P<sys_day>\S+)
    \s+(?P<sys_time>\S+)
    \s+(?P<server_ip>\S+)
    \s+(?P<client_ip>\S+)
    \s+\-
    \s+(?P<client_sesion>\S+)
    \s+\[(?P<req_datetime>\S+)
    \s+(?P<req_tz>\S+)\]
    \s+"(?P<req_method>\S+)\s(?P<req_uri>\S+)\s(?P<http_version>\S+)"
    \s+(?P<res_code>\S+)\s+(?P<res_bytes>\S+)
    \s+"(?P<ref_uri>[^"]*)"
    \s+"(?P<client_useragent>[^"]+)"
"""

class Error( Exception ):
    pass
class CorruptRecord( Error ):
    pass

class Parser( object ):

    def __init__( self, format = defaultreg, defaults = {} ):
        self.format = format
        r_format = format
        self.reggie = re.compile( format, re.X )
    def parse_line_shlex( self, line ):
        m = shlex.split( line )
        if len( m ) < 14:
            raise CorruptRecord( line )
        r = {}
        r[ "sys_month" ] = m[ 0 ]
        r[ "sys_day" ] = m[ 1 ]
        r[ "sys_time" ] = m[ 2 ]
        r[ "server_ip" ] = m[ 3 ]
        r[ "client_ip" ] = m[ 4 ]
        # skip -
        r[ "client_session" ] = m[ 6 ]
        r[ "req_datetime" ] = m[ 7 ][1:]
        r[ "req_tz" ] = m[ 8 ][:-1]
        r[ "req_method" ], r[ "req_uri" ], r[ "http_version" ] = m[ 9 ].split()
        r[ "res_code" ] = m[ 10 ]
        r[ "res_bytes" ] = m[ 11 ]
        r[ "ref_uri" ] = m[ 12 ]
        r[ "client_useragent" ] = m[ 13 ]
        return r

    def parse_line( self, line ):
        # use of match means format must occur at start of line
        m = self.reggie.match( line )
        if m:
            r = m.groupdict()
            return r
        raise CorruptRecord( line )

def parsetime( r ):
    r[ "req_datetime_struct" ] = time.strptime( r[ "req_datetime" ], "%d/%b/%Y:%H:%M:%S" )
    return r
def parsetimestamp( r ):
    if not r.has_key( "req_datetime_struct" ):
        parsetime( r )
    r[ "req_timestamp" ] = int( time.mktime( r[ "req_datetime_struct" ] ) )
    return r

if __name__ == "__main__":
    p = Parser()
    s = r'Jan 27 11:31:07 192.168.4.143 174.120.150.194 - - [27/Jan/2011:11:31:07 +0000] "GET http://www.eurogamer.net/articles/2011-01-27-source-ngp-battery-life-is-4-5-hours HTTP/1.1" 200 149787 "" "Mozilla/4.8 [en] (Windows NT 6.0; U)"'
    r = p.parse_line( s )
    print r

    #for ln in sys.stdin:
    #    r = p.parse_line( ln )
    #    print r

#Jan 27 11:31:07 192.168.4.143 174.120.150.194 - - [27/Jan/2011:11:31:07 +0000] "GET http://www.eurogamer.net/articles/2011-01-27-source-ngp-battery-life-is-4-5-hours HTTP/1.1" 200 149787 "" "Mozilla/4.8 [en] (Windows NT 6.0; U)"
#Jan 27 09:39:07 192.168.4.156 91.132.195.168 - - [27/Jan/2011:09:39:07 +0000] "GET http://www.eurogamer.net/articles/2011-01-27-source-ngp-battery-life-is-4-5-hours HTTP/1.1" 200 7404 "http://www.eurogamer.net/" "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)"
