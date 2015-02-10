crawler4py
==========
A web crawler in Python

Dependency List
==========
1. Lxml : https://pypi.python.org/pypi/lxml : html document parsing (Can remove in Config)
2. Python 2.6+ (The above dependency works on this version of python.
               You can try it on Python 3 too if you do not use the above dependency. Py3 has been Tested
               Note that there is a published version of lxml for Py 3.2 as of 9/16/2014.)


Config Variables
==========

MaxWorkerThreads : Number of Url Data Fetching Threads Allowed

FrontierTimeOut : Timeout(Seconds) for trying to get the next url from the frontier. 

WorkerTimeOut : Timeout(Seconds) for trying to get a free worker thread, (worker is taking too long maybe?)

OutBufferTimeOut : Timeout(Seconds) for getting data from the output queue

UrlFetchTimeOut : Timeout(Seconds) for getting data from a url

UserAgentString : The User Agent String that this crawler is going to identify itself as. http://tools.ietf.org/html/rfc2616#section-14.43 : HAVE TO DEFINE IN DERIVED CLASS

Resumable : To allow resume of fetching from last point of closure. Set to False to always restart from seed set of urls.

MaxRetryDownloadOnFail : Number of times to retry fetching a url if it fails

PolitenessDelay : PolitenessDelay that the crawler is forced to adhere to. http://en.wikipedia.org/wiki/Web_crawler#Politeness_policy

PersistentFile : The Persistent File to store current state of crawler for resuming (if Resumable is True)

NoOfDocToFetch : Total (Approximate) documents to fetch before stopping

MaxDepth : The Max Depth of the page to go to while fetching (depth = distance of first discovery from seed urls)

MaxPageSize : Max size of page in bytes that is allowed to be fetched. (Only works for websites that send Content-Length in response header)

MaxQueueSize : Max size of output queue. If the HandleData function is slow, then output buffer might not clear up fast.
               This enforces that the queue does not go beyond a certain size.
               Set to 0 if you want unlimited size
               Advantages of setting > 0: Fetch url waits for the buffer to become free when its full. If crawler crashes max of this size output is lost.
               Disadvantage of setting > 0: Slows down the crawling.

IgnoreRobotRule : This ignores the rules at robot.txt. Be very careful with this. Only make it True with permission of the host/API pulling that does not need robot rules.

DepthFirstTraversal : This sets the mode of traversal: False -> Breadth First, True -> Depth First.

RemoveJavaScriptAndCSS: If set to True, this removes all the Javascript and CSS inside the HTML page while the crawler is creating the corpus. This is used in the base implementation of GetTextData so if you override the function, this functionality might not work correctly. 

Config Functions
==========
GetSeeds [
  params : None
  Desc : Returns the first set of urls to start crawling from. HAVE TO DEFINE IN DERIVED CLASS
  return : list(str) : list of urls ]

HandleData [
  params : parsedData : parsedData = {"url" : "url", "text" : "text data from html", "html" : "raw html data"}
  Desc : Function to handle url data. Guaranteed to be Thread safe. Advisable to make this function light. Data can be massaged later. Storing data probably is more important.  HAVE TO DEFINE IN DERIVED CLASS
  return : None ]

AllowedSchemes [
  params : scheme : scheme/protocol to be testes : str 
  Desc : Function that allows the schemes/protocols in the set.
  return : bool (True if scheme is a valid scheme/protocol to fetch and process) ]

ValidUrl [
  params : url : url to check : str
  Desc : Function to determine if the url is a valid url that should be fetched or not. Default base class implementation returns True for all urls.
  return : bool (True if url is valid) ]
    
GetTextData [
  params : htmlData : raw html data : str
  Desc : Function to clean up html raw data and get the text from it. Keep it small. Not thread safe, returns an object that will go into the parsedData["text"] field for HandleData function above
  return : str ]

ExtractNextLinks [
  params : url : base url where the data was got from : str
           rawData : rawData obtained from the url : str
           outputLinks : the list of links that have been extracted from the rawData : list
  Desc : Function to extract the next links to iterate over. No need to validate the links.They get validated at the ValudUrl function when added to the frontier Add the output links to the outputLinks parameter (has to be a list). Return Bool signifying success of extracting the links. rawData for url will not be stored if this function returns False. If there are no links but the rawData is still valid and has to be saved return True    Keep this default implementation if you need all the html links from rawData
  return : bool ]

GetAuthenticationData [
  params : None
  Desc : Function that returns dict(top_level_url : tuple(username, password)) for basic authentication purposes
  return : dict(top_level_url : tuple(username, password)) ]

What to write
==========
1. Make a config file say MyCrawlerConfig.py at the same level as the Crawler4py folder (Not in that folder)
2. In that file make a class that inherits from Crawler4py.Config.
3. In the constructor define at least UserAgentString. You can set more of the above attributes here
4. define at least 2 functions: GetSeeds, HandleData. You can override more of the above functions here
5. In your main python file. from <Filename> import <Config Class name>
6. from Crawler4py.Crawler import Crawler
7. crawler = Crawler(<Config Class Name>())
8. crawler.StartCrawling()
