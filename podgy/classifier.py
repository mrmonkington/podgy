import sys
import re

"""
Classifies a URL as one of several types of URL

page
support
media
user defined types
    asset (content)
    ajax
unknown
"""

#defaultreg = """
#    \S+
#    \s+\S+
#    \s+\S+
#    \s+\S+
#    \s+\S+
#    \s+\-
#    \s+\S+
#    \s+\[\S+
#    \s+\S+\]
#    \s+"\S+\s\S+%s\s\S+"
#"""
#defaultreg = """
#    "(GET|POST)\s\S+%s\s\S+"
#"""

class Classifier:
    
    classes = []

    def __init__( self ):
        # order of specificity
        # once one matches it returns, so least specific matches come last
        self.classes = [
            ( re.compile( "(\.jpe?g|\.gif|\.png)($|\?)", re.I ), "media" ),
            ( re.compile( "(\.js|\.css|\.htc)($|\?)", re.I ), "support" ),
            ( re.compile( "(\.php|\.html|/)($|\?)", re.I ), "page" ),
            ( False, "unknown" )
        ]

        self.rawclasses = [
            ( re.compile( "\"(GET|POST)\s\S+(\.jpe?g|\.gif|\.png)(\??)", re.I | re.X ), "media" ),
            ( re.compile( "\"(GET|POST)\s\S+(\.js|\.css|\.htc)(\??)", re.I | re.X ), "support" ),
            ( re.compile( "\"(GET|POST)\s\S+(\.php|\.html|/)(\??)", re.I | re.X ), "page" ),
            ( False, "unknown" )
        ]
    def add_class( self, pattern, name, pattern_flags = re.I ):
        # TODO prepend user defined classifier
        self.classes.insert( 0, ( re.compile( pattern, pattern_flags ), name ) )

    def classify( self, req ):
        """Classifies based on record structure output from Parser.parse()
        """
        for c in self.classes:
            # a False pattern means we always match
            if not c[ 0 ] or c[ 0 ].search( req[ "req_uri" ] ):
                return c[ 1 ]
        raise Exception( "Couldn't classify this record, which is strange since there's a fallback.  This is a bug." )

    def classify_raw( self, line ):
        """Classifies based on raw log line - faster if you don't want to parse whole line first
        """
        for c in self.rawclasses:
            # a False pattern means we always match
            if not c[ 0 ] or c[ 0 ].search( line ):
                return c[ 1 ]
        raise Exception( "Couldn't classify this record, which is strange since there's a fallback.  This is a bug." )
        

if __name__ == "__main__":
    """A simple test
    """
    r = Classifier()
    s = r'Jan 27 11:31:07 192.168.4.143 174.120.150.194 - - [27/Jan/2011:11:31:07 +0000] "GET http://www.eurogamer.net/articles/2011-01-27-source-ngp-battery-life-is-4-5-hours HTTP/1.1" 200 149787 "" "Mozilla/4.8 [en] (Windows NT 6.0; U)"'
    print r.classify_raw( s )

    #v = r.classify( { "req_uri" : "fgdg.php" } )
    #print v
    #v = r.classify( { "req_uri" : "fgdg.html" } )
    #print v
    #v = r.classify( { "req_uri" : "fgdg.php?hi=monk" } )
    #print v
    #v = r.classify( { "req_uri" : "fgdg.php?ref=monk.gif" } )
    #print v
    #v = r.classify( { "req_uri" : "fgdg.jpg" } )
    #print v
    #v = r.classify( { "req_uri" : "fgdg.jpg?slide=true" } )
    #print v
    #r.add_class( "(\.jpe?g|\.gif|\.png)\?(.*&)?slideshow=true(&|$)", "slideshow" )
    #v = r.classify( { "req_uri" : "fgdg.jpg?slideshow=true" } )
    #print v
