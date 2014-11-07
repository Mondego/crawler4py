'''
@Author: Rohan Achar ra.rohan@gmail.com
'''

import sys
from abc import *

class Config:
    __metaclass__ = ABCMeta

    def __init__(self):
        #Number of Url Data Fetching Threads Allowed
        self.MaxWorkerThreads = 2

        #Timeout(Seconds) for trying to get the next url from the frontier. 
        self.FrontierTimeOut = 10

        #Timeout(Seconds) for trying to get a free worker thread, (worker is taking too long maybe?)
        self.WorkerTimeOut = 60

        #Timeout(Seconds) for getting data from the output queue
        self.OutBufferTimeOut = 60

        #Timeout(Seconds) for getting data from a url
        self.UrlFetchTimeOut = 2

        #The User Agent String that this crawler is going to identify itself as. http://tools.ietf.org/html/rfc2616#section-14.43
        self.__UserAgentString = "INF221 - Class project - Privacy"

        #To allow resume of fetching from last point of closure. Set to False to always restart from seed set of urls.
        self.Resumable = False

        #Number of times to retry fetching a url if it fails
        self.MaxRetryDownloadOnFail = 5

        #PolitenessDelay that the crawler is forced to adhere to. http://en.wikipedia.org/wiki/Web_crawler#Politeness_policy
        self.PolitenessDelay = 300

        #The Persistent File to store current state of crawler for resuming (if Resumable is True)
        self.PersistentFile = "Persistent.shelve"

        #Total (Approximate) documents to fetch before stopping
        self.NoOfDocToFetch = 100

        #The Max Depth of the page to go to while fetching (depth = distance of first discovery from seed urls)
        self.MaxDepth = 5

        #Max size of page in bytes that is allowed to be fetched. (Only works for websites that send Content-Length in response header)
        self.MaxPageSize = 1048576

        #Max size of output queue. If the HandleData function is slow, then output buffer might not clear up fast.
        #This enforces that the queue does not go beyond a certain size.
        #Set to 0 if you want unlimited size
        #Advantages of setting > 0: Fetch url waits for the buffer to become free when its full. If crawler crashes max of this size output is lost.
        #Disadvantage of setting > 0: Slows down the crawling.
        self.MaxQueueSize = 10

        #This ignores the rules at robot.txt. Be very careful with this. Only make it True with permission of the host/API pulling that does not need robot rules.
        self.IgnoreRobotRule = False

        #This sets the mode of traversal: False -> Breadth First, True -> Depth First.
        self.DepthFirstTraversal = False
        
        #This tells the cralwer to remove the Javascript and CSS data from an html document before stripping the tags off.
        self.RemoveJavaScriptAndCSS = False

    def ValidateConfig(self):
        '''Validates the config to see if everything is in order. No need to extend this'''
        try:
            assert (self.UserAgentString != "" or self.UserAgentString != "Set This Value!")
        except AssertionError:
            print ("Set value of UserAgentString")
            sys.exit(1)
        try:
            assert (self.MaxWorkerThreads != 0)
        except AssertionError:
            print ("MaxWorkerThreads cannot be 0")
            sys.exit(1)
        

    @abstractmethod
    def GetSeeds(self):
        '''Returns the first set of urls to start crawling from'''
        return ["http://neerajkumar.net/about", "http://geeksforgeeks.org"]

    @abstractmethod
    def HandleData(self, parsedData):
        '''Function to handle url data. Guaranteed to be Thread safe.
        parsedData = {"url" : "url", "text" : "text data from html", "html" : "raw html data"}
        Advisable to make this function light. Data can be massaged later. Storing data probably is more important'''
        print (parsedData["url"])
        pass

    def AllowedSchemes(self, scheme):
        '''Function that allows the schemes/protocols in the set.'''
        return scheme.lower() in set(["http", "https", "ftp", b"http", b"https", b"ftp"])

    @abstractmethod
    def ValidUrl(self, url):
        '''Function to determine if the url is a valid url that should be fetched or not.'''
        return True
        
    def GetTextData(self, htmlData):
        '''Function to clean up html raw data and get the text from it. Keep it small.
        Not thread safe, returns an object that will go into the parsedData["text"] field for HandleData function above'''
        from lxml import html
        if ( self.RemoveJavaScriptAndCSS ):
          try:
            from lxml.html.clean import Cleaner
            cleaner = Cleaner()
            cleaner.javascript = True
            cleaner.style = True
            htmlData = cleaner.clean_html(htmlData)
          except:
            print("Could not remove style and js code")
        return html.fromstring(htmlData).text_content()

    def ExtractNextLinks(self, url, rawData, outputLinks):
        '''Function to extract the next links to iterate over. No need to validate the links. They get validated at the ValudUrl function when added to the frontier
        Add the output links to the outputLinks parameter (has to be a list). Return Bool signifying success of extracting the links.
        rawData for url will not be stored if this function returns False. If there are no links but the rawData is still valid and has to be saved return True
        Keep this default implementation if you need all the html links from rawData'''

        from lxml import html,etree

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

    def GetAuthenticationData(self):
        ''' Function that returns dict(top_level_url : tuple(username, password)) for basic authentication purposes'''
        return {}