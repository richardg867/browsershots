"""
A robot exclusion rules parser for Python by Philip Semanchuk
v0.9.4
Full documentation, examples and a comparison to Python's robotparser module here:
http://NikitaTheSpider.com/articles/rerp.html

This code is released under GPL 2.0.
http://www.gnu.org/copyleft/gpl.html

Comments, bug reports, etc. are most welcome via email to:  first name @ last name .com
or use this: 'cGhpbGlwQHNlbWFuY2h1ay5jb20=\n'.decode('base64')

Simple usage examples:

    import robotexclusionrulesparser
    
    rerp = robotexclusionrulesparser.RobotExclusionRulesParser()

    try:
        rerp.fetch('http://www.example.com/robots.txt')
    except:
        # See the documentation for expected errors
    
    if rerp.is_allowed('CrunchyFrogBot', 'http://example.com/foo.html'):
        # It is OK to fetch /foo.html

OR supply the contents of robots.txt yourself:

    rerp = RobotExclusionRulesParser()
    s = file("robots.txt").read()
    rerp.parse(s)
    
    if rerp.is_allowed('CrunchyFrogBot', 'http://example.com/foo.html'):
        # It is OK to fetch /foo.html

The function is_expired() tells you if you need to fetch a fresh copy of this robots.txt.
    
    if rerp.is_expired():
        # Get a new copy


RobotExclusionRulesParser supports __str()__ so you can print an instance to see the its
rules in robots.txt format.

The comments refer to MK1994 and MK1996. These are:
MK1994 = the 1994 robots.txt draft spec (http://www.robotstxt.org/wc/norobots.html)
MK1996 = the 1996 robots.txt draft spec (http://www.robotstxt.org/wc/norobots-rfc.html)

"""

import urllib
import urllib2
import urlparse
import re
import time
import rfc822
import calendar

_EndOfLineRegex = re.compile(r"(?:\r\n)|\r|\n")

# This regex is a little more generous than the spec because it accepts "User-agent" or
# "Useragent" (without a dash). MK1994/96 permits only the former. The regex also doesn't 
# insist that "useragent" is at the exact beginning of the line, which makes this code immune
# to confusion caused by byte order markers. 
_ExclusionLineRegex = re.compile("(allow|disallow|user[-]?agent):[ \t]*(.*)", re.IGNORECASE)

# This is the number of seconds in a week that I use to determine the default 
# expiration date defined in MK1996.
SEVEN_DAYS = 60 * 60 * 24 * 7

# This controls the max number of bytes read in as a robots.txt file. This is just a 
# bit of defensive programming in case someone accidentally sends an ISO file in place
# of their robots.txt. (It happens...)  Suggested by Dima Brodsky.
MAX_FILESIZE = 100 * 1024   # 100k 

# Control characters are everything < 0x20 and 0x7f. 
_ControlCharactersRegex = re.compile(r"""[\000-\037]|\0177""")

# Charset extraction regex for pulling the encoding (charset) out of a content-type header.
_CharsetExtractionRegex = re.compile(r"""charset=['"]?(?P<encoding>[^'"]*)['"]?""")

def _ScrubData(s):
    # Data is either a path or user agent name; i.e. the data portion of a robots.txt line.
    # Scrubbing it consists of (a) removing extraneous whitespace, (b) turning tabs into 
    # spaces (path and UA names should not contain tabs), and (c) stripping control characters
    # which, like tabs, shouldn't be present. (See MK1996 section 3.3 "Formal Syntax".)
    s = _ControlCharactersRegex.sub("", s)
    s = s.replace("\t", " ")
    return s.strip()
    
    
def _ParseContentTypeHeader(header):
    MediaType = ""
    encoding = ""

    # A typical content-type looks like this:    
    #    text/plain; charset=UTF-8
    # The portion after "text/plain" is often not present.
    # ref: http://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html#sec3.7

    if header:
        header = header.strip().lower()
    else:
        header = ""
       
    # I use a lambda here instead of passing strip directly because I don't know if I'm 
    # dealing with str or unicode objects.
    chunks = map(lambda s: s.strip(), header.split(";"))
    MediaType = chunks[0]
    if len(chunks) > 1:
        for parameter in chunks[1:]:
            m = _CharsetExtractionRegex.search(parameter)
            if m and m.group("encoding"):
                encoding = m.group("encoding")

    return MediaType.strip(), encoding.strip()

    
class RobotExclusionRulesParser(object):
    
    def __init__(self):
        self._source_url = ""
        self.user_agent = None
        self.use_local_time = True
        self.expiration_date = self._now() + SEVEN_DAYS
        
        self.__rulesets = [ ]
        

    # source_url is read-only.
    def __get_source_url(self):
        return self._source_url

    def __set_source_url(self, foo):
        raise AttributeError

    source_url = property(__get_source_url, __set_source_url)
                            

    def _now(self):
        if self.use_local_time:
            return time.time()
        else:
            # What the heck is timegm() doing in the calendar module?!?
            return calendar.timegm(time.gmtime())


    def is_expired(self):
        return self.expiration_date <= self._now()     


    def is_allowed(self, user_agent, url):
        # The robot rules are stored internally as Unicode. The two lines below ensure that
        # the parameters passed to this function are also Unicode. If those lines were not
        # present and the caller passed a non-Unicode user agent or URL string to this 
        # function, Python would silently convert it to Unicode before comparing it to the 
        # robot rules. Such conversions use the default encoding (usually US-ASCII) and if 
        # the string couldn't be converted using that encoding, Python would raise a 
        # UnicodeError later on in the guts of this code which would be confusing. Converting
        # the strings to Unicode here doesn't make the problem go away but it does make 
        # the conversion explicit so that failures are easier to understand. 
        if not isinstance(user_agent, unicode): user_agent = unicode(user_agent)
        if not isinstance(url, unicode): url = unicode(url)
    
        for ruleset in self.__rulesets:
            if ruleset.does_user_agent_match(user_agent):
                return ruleset.is_url_allowed(url)
                
        return True


    def fetch(self, url):
        # iso-8859-1 is the default encoding for text files per the specs for HTTP 1.0 (RFC 
        # 1945 sec 3.6.1) and HTTP 1.1 (RFC 2616 sec 3.7.1).
        # ref: http://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html#sec3.7.1
        encoding = "iso-8859-1"
        content = ""
        ExpiresHeader = None
        ContentTypeHeader = None

        self._source_url = url
        
        if self.user_agent:
            req = urllib2.Request(url, None, { 'User-Agent' : self.user_agent })
        else:
            req = urllib2.Request(url)

        try:
            f = urllib2.urlopen(req)
            content = f.read(MAX_FILESIZE)
            ExpiresHeader = f.info().getdate_tz("expires")
            ContentTypeHeader = f.info().getheader("Content-Type")
            f.close()
            ResponseCode = 200
        except urllib2.URLError, ErrorInstance:
            # Not all errors return an HTTP response code.
            if hasattr(ErrorInstance, "code"):
                ResponseCode = ErrorInstance.code
            else:
                ResponseCode = -1
                
        # MK1996 section 3.4 says, "...robots should take note of Expires header set by the 
        # origin server. If no cache-control directives are present robots should default 
        # to an expiry of 7 days".
        self.expiration_date = None
        if ResponseCode == 200:
            self.expiration_date = ExpiresHeader
            if self.expiration_date:
                # I don't know what timezone this date uses and I want to let Python convert it 
                # to UTC for me. The UTC offset is encoded in the 10th element of the tuple
                # that getdate_tz() returns. That function expresses the offset in seconds 
                # while rfc822.mktime_tz() expects it to be in hours. Furthermore, getdate_tz()
                # has the undocumented feature of occasionally returning None in that element.
                offset = self.expiration_date[9]
                if offset is None: offset = 0
                self.expiration_date = self.expiration_date[:9] + ((offset / 3600.0),)
                
                self.expiration_date = rfc822.mktime_tz(self.expiration_date)
                if self.use_local_time: 
                    # I have to do a little more converting to get this UTC timestamp 
                    # into localtime.
                    self.expiration_date = time.mktime(time.gmtime(self.expiration_date)) 

        if not self.expiration_date: self.expiration_date = self._now() + SEVEN_DAYS

        if (ResponseCode >= 200) and (ResponseCode < 300):
            # All's well.
            MediaType, encoding = _ParseContentTypeHeader(ContentTypeHeader)
            if not encoding: encoding = "iso-8859-1"
            
        elif ResponseCode in (401, 403):
            # 401 or 403 ==> Go away or I will taunt you a second time!
            content = "User-agent: *\nDisallow: /"
        elif ResponseCode == 404:
            # No robots.txt ==> everyone's welcome
            content = ""
        else:        
            # Uh-oh. I punt this up to the caller. 
            raise urllib2.URLError(ResponseCode)
        
        # Unicode decoding errors are another point of failure that I punt up to the caller.
        try:
            content = unicode(content, encoding)
        except UnicodeError:
            raise UnicodeError("Robots.txt contents are not in the encoding expected (%s)." % encoding)
        except (LookupError, ValueError):
            # LookupError ==> Python doesn't have a decoder for that encoding. One can also
            # get a ValueError here if the encoding starts with a dot (ASCII 0x2e). See
            # Python bug 1446043 for details. This bug was supposedly fixed in Python 2.5.
            raise UnicodeError("I don't understand the encoding \"%s\"." % encoding)
        
        # Now that I've fetched the content and turned it into Unicode, I can parse it.
        self.parse(content)
        
        
    def parse(self, s):
        self.__rulesets = [ ]
        
        if not isinstance(s, unicode): s = unicode(s, "iso-8859-1")
    
        # Normalize newlines.
        s = _EndOfLineRegex.sub("\n", s)
        
        lines = s.split("\n")
        
        PreviousLineWasAUserAgent = False
        CurrentRuleset = None
        
        for line in lines:
            line = line.strip()
            
            if line and line[0] == '#':
                # "Lines containing only a comment are discarded completely, and therefore 
                # do not indicate a record boundary." (MK1994)
                pass
            else:
                # Remove comments
                i = line.find("#")
                if i != -1: line = line[:i]
        
                line = line.strip()
                
                if line == '':
                    # An empty line indicates the end of a ruleset.
                    if CurrentRuleset and CurrentRuleset.is_not_empty():
                        self.__rulesets.append(CurrentRuleset)
                    
                    CurrentRuleset = None
                    PreviousLineWasAUserAgent = False
                else:                    
                    # Each line can be separated into one of four categories:
                    # 1) User-agent: blah blah blah
                    # 2) Disallow: blah blah blah
                    # 3) Allow: blah blah blah
                    # 4) Everything else
                    # 1 - 3 are interesting and I find them with the regex below. Category 4 I 
                    # discard as directed by the MK1994 ("Unrecognised headers are ignored.")
                    matches = _ExclusionLineRegex.findall(line)
                    
                    # Categories 1 - 3 produce two matches, #4 produces none.
                    if matches:
                        field, data = matches[0]
                        field = field.lower()
                        data = _ScrubData(data)

                        # Matching "useragent" is a deviation from the MK1994/96 which permits 
                        # only "user-agent".
                        if field in ("useragent", "user-agent"):
                            if PreviousLineWasAUserAgent:
                                # Add this UA to the current ruleset 
                                if CurrentRuleset and data:
                                    CurrentRuleset.add_robot_name(data)
                            else:
                                # Save the current ruleset and start a new one.
                                if CurrentRuleset and CurrentRuleset.is_not_empty():
                                    self.__rulesets.append(CurrentRuleset)
                                #else:
                                    # (is_not_empty() == False) ==> malformed robots.txt listed
                                    # a UA line but provided no name or didn't provide any 
                                    # rules for a named UA.
                                CurrentRuleset = ruleset()
                                if data: 
                                    CurrentRuleset.add_robot_name(data)
                            
                            PreviousLineWasAUserAgent = True
                        elif field == "allow":
                            PreviousLineWasAUserAgent = False
                            if CurrentRuleset:
                                CurrentRuleset.add_allow_rule(data)
                        else:
                            PreviousLineWasAUserAgent = False
                            # This is a disallow line
                            if CurrentRuleset:
                                CurrentRuleset.add_disallow_rule(data)
                    
        if CurrentRuleset and CurrentRuleset.is_not_empty():
            self.__rulesets.append(CurrentRuleset)
            
        # Now that I have all the rulesets, I want to order them in a way that makes 
        # comparisons easier later. Specifically, any ruleset that contains the default
        # user agent '*' should go at the end of the list so that I only apply the default
        # as a last resort. According to MK1994/96, there should only be one ruleset that 
        # specifies * as the user-agent, but you know how these things go.
        NotDefaults = filter(lambda ruleset: not ruleset.is_default(), self.__rulesets) or [ ]
        Defaults = filter(lambda ruleset: ruleset.is_default(), self.__rulesets) or [ ]

        self.__rulesets = NotDefaults + Defaults

    
    def __str__(self):
        s = ""
        for ruleset in self.__rulesets:
            s += str(ruleset) + "\n"
        
        return s


class ruleset(object):
    ALLOW = 1
    DISALLOW = 2
    
    def __init__(self):
        self.RobotNames = [ ]
        self.rules = [ ]
    
    def __str__(self):
        s = ""
        for RobotName in self.RobotNames:
            s += "User-agent: %s \n" % RobotName
        for rule in self.rules:
            type, path = rule
            if type == self.ALLOW:
                s += "Allow: "
            else:
                s += "Disallow: "
            s += "%s\n" % path
        
        return s.encode("utf-8")
    
    
    def _unquote_path(self, path):
        # MK1996 says, 'If a %xx encoded octet is encountered it is unencoded prior to 
        # comparison, unless it is the "/" character, which has special meaning in a path.'
        path = re.sub("%2[fF]", "\n", path)
        path = urllib.unquote(path)
        return path.replace("\n", "%2F")

    
    def add_robot_name(self, bot):
        self.RobotNames.append(bot)
        
    def add_allow_rule(self, path):
        self.rules.append((self.ALLOW, self._unquote_path(path)))
        
    def add_disallow_rule(self, path):
        self.rules.append((self.DISALLOW, self._unquote_path(path)))
        
    def is_not_empty(self):
        return bool(len(self.rules)) and bool(len(self.RobotNames))
    
    def is_default(self):
        return bool('*' in self.RobotNames)
    
    def does_user_agent_match(self, user_agent):
        match = False
        
        for RobotName in self.RobotNames:
            # MK1994 says, "A case insensitive substring match of the name without version 
            # information is recommended." MK1996 3.2.1 states it even more strongly: "The
            # robot must obey the first record in /robots.txt that contains a User-Agent 
            # line whose value contains the name token of the robot as a substring. The 
            # name comparisons are case-insensitive."
            match = match or (RobotName == '*') or (user_agent.lower().find(RobotName.lower()) != -1)
                    
        return match

    def is_url_allowed(self, url):
        allowed = True
        
        # Schemes and host names are not part of the robots.txt protocol, so I ignore them. 
        # It is the caller's responsibility to make sure they match.
        scheme, host, path, parameters, query, fragment = urlparse.urlparse(url)
        url = urlparse.urlunparse(("", "", path, parameters, query, fragment))

        url = self._unquote_path(url)
        
        done = False
        i = 0
        while not done:
            RuleType, path = self.rules[i]

            if url.startswith(path):
                # Ding!
                done = True
                allowed = (RuleType == self.ALLOW)
                # A blank path means "nothing", so that effectively negates the value above.
                # e.g. "Disallow:   " means allow everything
                if path == '': allowed = not allowed

            i += 1
            if i == len(self.rules):
                done = True
                
        return allowed        
