'''
@Author: Rohan Achar ra.rohan@gmail.com
'''
try:
    import robotparser
    from urlparse import urlparse, parse_qs
except ImportError:
    import urllib.robotparser as robotparser
    from urllib.parse import urlparse, parse_qs


# Not stored in persistent storage beacuse the robots.txt could have changed across runs.
class Robot:
    def __init__(self, config):
        self.RuleDict = {}
        self.config = config    

    def Allowed(self, url):
        if self.config.IgnoreRobotRule:
            return True
        try:
            parsed = urlparse(url)
            port = ""
            if (parsed.port):
                port = ":" + str(parsed.port)
        except ValueError:
            print ("ValueError: " + url)

        try:
            roboturl = parsed.scheme + "://" + parsed.hostname + port + "/robots.txt"
        except TypeError:
            print (parsed)
        if roboturl not in self.RuleDict:
            self.RuleDict[roboturl] = robotparser.RobotFileParser(roboturl)
            try:
                self.RuleDict[roboturl].read()
            except IOError:
                del self.RuleDict[roboturl]
                return True
            
        try:
            return self.RuleDict[roboturl].can_fetch(self.config.UserAgentString, url)
        except KeyError:
            print ("Keyerror: " + url)
            return True


        