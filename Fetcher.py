'''
@Author: Rohan Achar ra.rohan@gmail.com
'''

import nltk
import urllib2, httplib
import socket, base64

import Config

from threading import *
from urlparse import urlparse,parse_qs

#url is assumed to be crawlable
def FetchUrl(url, depth, urlManager, retry = 0):
    urlreq = urllib2.Request(url, None, {"User-Agent" : Config.UserAgentString})
    parsed = urlparse(url) 
    if parsed.hostname in Config.GetAuthenticationData():
        username, password = Config.GetAuthenticationData()[parsed.hostname]
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        urlreq.add_header("Authorization", "Basic %s" % base64string)
    try:    
        urldata = urllib2.urlopen(urlreq, timeout = Config.UrlFetchTimeOut)
        try:
            size = int(urldata.info().getheaders("Content-Length")[0])
            
        except IndexError:
            size = -1

        return size < Config.MaxPageSize and urldata.code > 199 and urldata.code < 300 and ProcessUrlData(url, urldata.read(), depth, urlManager)
    except urllib2.HTTPError, e:
        print (e.headers)
        return False
    except urllib2.URLError, e:
        return False
    except httplib.HTTPException, e:
        return False
    except socket.error:
        if (retry == Config.MaxRetryDownloadOnFail):
            return False
        print ("Retrying " + url + " " + str(retry + 1) + " time")
        return FetchUrl(url, depth, urlManager, retry + 1)
    
def ProcessUrlData(url, htmlData, depth, urlManager):
    textData = Config.GetTextData(htmlData)
    links = []
    if (Config.ExtractNextLinks(url, htmlData, links)):
        urlManager.AddOutput({"html": htmlData, "text": textData, "url": url})
        for link in links:
            urlManager.AddToFrontier(link, depth + 1)
        return True
    return False    