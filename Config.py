'''
@Author: Rohan Achar ra.rohan@gmail.com
'''

import re, nltk
from urlparse import urlparse,parse_qs
from lxml import html,etree

#Number of Url Data Fetching Threads Allowed
MaxWorkerThreads = 8

#Timeout(Seconds) for trying to get the next url from the frontier. 
FrontierTimeOut = 60

#Timeout(Seconds) for trying to get a free worker thread, (worker is taking too long maybe?)
WorkerTimeOut = 60

#Timeout(Seconds) for getting data from the output queue
OutBufferTimeOut = 60

#Timeout(Seconds) for getting data from a url
UrlFetchTimeOut = 2

#The User Agent String that this crawler is going to identify itself as. http://tools.ietf.org/html/rfc2616#section-14.43
UserAgentString = "Set This Value!"

#To allow resume of fetching from last point of closure. Set to False to always restart from seed set of urls.
Resumable = True

#Number of times to retry fetching a url if it fails
MaxRetryDownloadOnFail = 5

#PolitenessDelay that the crawler is forced to adhere to. http://en.wikipedia.org/wiki/Web_crawler#Politeness_policy
PolitenessDelay = 300

#The Persistent File to store current state of crawler for resuming (if Resumable is True)
PersistentFile = "Persistent.shelve"

#Total (Approximate) documents to fetch before stopping
NoOfDocToFetch = -1

#The Max Depth of the page to go to while fetching (depth = distance of first discovery from seed urls)
MaxDepth = -1

#Max size of page in bytes that is allowed to be fetched. (Only works for websites that send Content-Length in response header)
MaxPageSize = 1048576

#Max size of output queue. If the HandleData function is slow, then output buffer might not clear up fast.
#This enforces that the queue does not go beyond a certain size.
#Set to 0 if you want unlimited size
#Advantages of setting > 0: Fetch url waits for the buffer to become free when its full. If crawler crashes max of this size output is lost.
#Disadvantage of setting > 0: Slows down the crawling.
MaxQueueSize = 0

#This ignores the rules at robot.txt. Be very careful with this. Only make it True with permission of the host/API pulling that does not need robot rules.
IgnoreRobotRule = False


def GetSeeds():
    '''Returns the first set of urls to start crawling from'''
    return ["Sample Url 1", "Sample Url 2", "Etc"]

def HandleData(parsedData):
    '''Function to handle url data. Guaranteed to be Thread safe.
    parsedData = {"url" : "url", "text" : "text data from html", "html" : "raw html data"}
    Advisable to make this function light. Data can be massaged later. Storing data probably is more important'''
    print (parsedData["url"])
    pass

def AllowedSchemes(scheme):
    '''Function that allows the schemes/protocols in the set.'''
    return scheme.lower() in set(["http", "https", "ftp"])

def ValidUrl(url):
    '''Function to determine if the url is a valid url that should be fetched or not.'''
    parsed = urlparse(url)
    try:
        return ".ics.uci.edu" in parsed.hostname \
            and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico|png|tiff?|mid|mp2|mp3|mp4)$", parsed.path)

    except TypeError:
        print ("TypeError for ", parsed)

def GetTextData(htmlData):
    '''Function to clean up html raw data and get the text from it. Keep it small.
    Not thread safe, returns an object that will go into the parsedData["text"] field for HandleData function above'''
    return nltk.clean_html(htmlData)

def ExtractNextLinks(url, rawData, outputLinks):
    '''Function to extract the next links to iterate over. No need to validate the links. They get validated at the ValudUrl function when added to the frontier
    Add the output links to the outputLinks parameter (has to be a list). Return Bool signifying success of extracting the links.
    rawData for url will not be stored if this function returns False. If there are no links but the rawData is still valid and has to be saved return True
    Keep this default implementation if you need all the html links from rawData'''

    try:
        htmlParse = html.document_fromstring(rawData)
        htmlParse.make_links_absolute(url)
    except etree.ParserError:
        return False
    except etree.XMLSyntaxError:
        return False
    
    for element, attribute, link, pos in htmlParse.iterlinks():
        outputLinks.append(link)
    return True

def GetAuthenticationData():
    ''' Function that returns dict(top_level_url : tuple(username, password)) for basic authentication purposes'''
    return {}