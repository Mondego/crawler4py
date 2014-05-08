'''
@Author: Rohan Achar ra.rohan@gmail.com
'''

import nltk
import urllib2, httplib
import socket

import Config

from threading import *
from lxml import html,etree
from urlparse import urlparse,parse_qs

#url is assumed to be crawlable
def FetchUrl(url, depth, urlManager, retry = 0):
    print(url)
    urlreq = urllib2.Request(url, None, {"User-Agent" : Config.UserAgentString})
    try:    
        
        urldata = urllib2.urlopen(urlreq, timeout = Config.UrlFetchTimeOut)
        try:
            size = int(urldata.info().getheaders("Content-Length")[0])
        except IndexError:
            size = -1

        return size < Config.MaxPageSize and urldata.code > 199 and urldata.code < 300 and ProcessUrlData(url, urldata.read(), depth, urlManager)
    except urllib2.HTTPError:
        return False
    except urllib2.URLError:
        return False
    except httplib.HTTPException:
        return False
    except socket.error:
        if (retry == Config.MaxRetryDownloadOnFail):
            return False
        print "Retrying ", url, " ", retry + 1, " time"
        return FetchUrl(url, depth, urlManager, retry + 1)
    
def ProcessUrlData(url, htmlData, depth, urlManager):
    textData = Config.GetTextData(htmlData)
    try:
        htmlParse = html.document_fromstring(htmlData)
        htmlParse.make_links_absolute(url)
    except etree.ParserError:
        return False
    except etree.XMLSyntaxError:
        return False
    
    urlManager.AddOutput({"html": htmlData, "text": textData, "url": url})
    for element, attribute, link, pos in htmlParse.iterlinks():
        urlManager.AddToFrontier(link, depth + 1)
    
    return True
    