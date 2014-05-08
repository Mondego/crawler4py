crawler4py
==========

A web crawler in Python

==========
Dependency List
==========
1. NLTK : http://www.nltk.org/install.html (You can remove this dependency in Config.py if you want)
2. Lxml : https://pypi.python.org/pypi/lxml (Required)

==========
Config Variables
==========

MaxWorkerThreads : Number of Url Data Fetching Threads Allowed

FrontierTimeOut : Timeout(Seconds) for trying to get the next url from the frontier. 

WorkerTimeOut : Timeout(Seconds) for trying to get a free worker thread, (worker is taking too long maybe?)

OutBufferTimeOut : Timeout(Seconds) for getting data from the output queue

UrlFetchTimeOut : Timeout(Seconds) for getting data from a url

UserAgentString : The User Agent String that this crawler is going to identify itself as. http://tools.ietf.org/html/rfc2616#section-14.43

Resumable : To allow resume of fetching from last point of closure. Set to False to always restart from seed set of urls.

MaxRetryDownloadOnFail : Number of times to retry fetching a url if it fails

PolitenessDelay: PolitenessDelay that the crawler is forced to adhere to. http://en.wikipedia.org/wiki/Web_crawler#Politeness_policy

PersistentFile : The Persistent File to store current state of crawler for resuming (if Resumable is True)

NoOfDocToFetch : Total (Approximate) documents to fetch before stopping

MaxDepth : The Max Depth of the page to go to while fetching (depth = distance of first discovery from seed urls)

MaxPageSize : Max size of page in bytes that is allowed to be fetched. (Only works for websites that send Content-Length in response header)

MaxQueueSize : Max size of output queue. If the HandleData function is slow, then output buffer might not clear up fast.
               This enforces that the queue does not go beyond a certain size.
               Set to 0 if you want unlimited size
               Advantages of setting > 0: Fetch url waits for the buffer to become free when its full. If crawler crashes max of this size output is lost.
               Disadvantage of setting > 0: Slows down the crawling.

Seeds : Initial set of urls to start crawling from

==========
Config Functions
==========
HandleData 
  params : parsedData : parsedData = {"url" : "url", "text" : "text data from html", "html" : "raw html data"}
  Desc : Function to handle url data. Guaranteed to be Thread safe. Advisable to make this function light. Data can be massaged later. Storing data probably is more important
  return : None

AllowedSchemes 
  params : scheme : scheme/protocol to be testes : str 
  Desc : Function that allows the schemes/protocols in the set.
  return : bool (True if scheme is a valid scheme/protocol to fetch and process)

ValidUrl 
  params : url : url to check : str
  Desc : Function to determine if the url is a valid url that should be fetched or not.
  return : bool (True if url is valid)
    
GetTextData 
  params : htmlData : raw html data : str
  Desc : Function to clean up html raw data and get the text from it. Keep it small. Not thread safe, returns an object that will go into the parsedData["text"] field for HandleData function above
  return : str


==========
What to write
==========
Modify the above variables and functions in Config.py

==========
How to run it
==========
python Crawler4py.py

