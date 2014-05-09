'''
@Author: Rohan Achar ra.rohan@gmail.com
'''

import robotparser
import urllib2

import Config

from urlparse import urlparse,parse_qs

# Not stored in persistent storage beacuse the robots.txt could have changed across runs.
RuleDict = {}

def Allowed(url):
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
    if roboturl not in RuleDict:
        RuleDict[roboturl] = robotparser.RobotFileParser(roboturl)
        try:
            RuleDict[roboturl].read()
        except IOError:
            del RuleDict[roboturl]
            return True
            
    try:
        return RuleDict[roboturl].can_fetch(Config.UserAgentString, url)
    except KeyError:
        print ("Keyerror: " + url)
        return True


        