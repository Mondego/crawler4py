'''
@Author: Rohan Achar ra.rohan@gmail.com
'''

import os, shelve, urlparse, re

from Queue import Queue, Empty, Full
from sets import Set
from threading import Lock

import Robot, Config

class UrlManager:
    def __init__(self):
        self.Frontier = Set()
        self.Working = Set()
        self.Done = Set()
        self.Output = Queue(Config.MaxQueueSize)
        self.FrontierLock = Lock()
        self.WorkingLock = Lock()
        self.DoneLock = Lock()
        self.ShelveLock = Lock()
        self.DocumentCount = 0
        self.ShelveObj = None
        self.__Init()
        

    def __Init(self):
        self.ShelveObj = None
        if Config.Resumable:
            if (os.access(Config.PersistentFile, os.F_OK)):
                self.ShelveObj = shelve.open(Config.PersistentFile)
                keys = self.ShelveObj.keys()
                if len(keys) > 0:
                    for key in keys:
                        if not self.ShelveObj[key][0]:
                            self.Frontier.add((key, self.ShelveObj[key][1]))
                    return

            self.ShelveObj = shelve.open(Config.PersistentFile)

        for url in Config.Seeds:
            self.AddToFrontier(url, 0)
        
        return


    def __CleanUrl(self, url):
        parsedset = urlparse.urlparse(url)
        parsedset = parsedset._replace(fragment = "")
        if parsedset.path != "" and parsedset.path[-1] != "/":
            pathparts = parsedset.path.split("/")
            if (len(pathparts) > 1):
                lastpart = pathparts[-1]
                if (re.match("index\..", lastpart)):
                    pathparts = pathparts[:-1]
            parsedset = parsedset._replace(path = ("/".join(pathparts)).rstrip("/"))
            url = urlparse.urlunparse(parsedset)
        return url.rstrip("/")

    def __Valid(self, url, depth):
        parsedset = urlparse.urlparse(url)
        return Config.AllowedSchemes(parsedset.scheme)\
            and Robot.Allowed(url)\
            and Config.ValidUrl(url)\
            and (depth <= Config.MaxDepth or Config.MaxDepth <= 0)\
            and (self.DocumentCount <= Config.NoOfDocToFetch or Config.NoOfDocToFetch <= 0)

    def __IsShelveVisited(self, url):
        return self.ShelveObj.has_key(url)

    def AddToFrontier(self, url, depth):
        url = self.__CleanUrl(url)
        if not self.__Valid(url, depth):
            return False

        complete = False
        with self.ShelveLock, self.FrontierLock, self.WorkingLock, self.DoneLock:
            shelved = False
            if Config.Resumable:
                if self.__IsShelveVisited(url):
                    shelved = True
            
            if not shelved and url not in self.Frontier and url not in self.Working and url not in self.Done:
                self.Frontier.add((url, depth))
                if Config.Resumable:
                    self.ShelveObj[url] = (False, depth)
                    self.ShelveObj.sync()
                complete = True

        return complete

    def GetFromFrontier(self):
        obtained = False
        url = ""
        depth = 0
        with self.FrontierLock, self.WorkingLock:
            if len(self.Frontier) != 0:
                url, depth = self.Frontier.pop()
                self.Working.add(url)
                obtained = True

        return obtained, url, depth

    def MarkUrlAsDone(self, url):
        with self.ShelveLock, self.WorkingLock, self.DoneLock:
            self.DocumentCount += 1
            self.Working.remove(url)
            self.Done.add(url)
            if Config.Resumable:
                depth = self.ShelveObj[url][1]
                self.ShelveObj[url] = (True, depth)
                self.ShelveObj.sync()


    def AddOutput(self, data):
        self.Output.put(data)

    def GetOutput(self):
        try:
            return (True, self.Output.get(True, Config.OutBufferTimeOut))
        except Empty:
            print ("No value in Output buffer for " + str(Config.OutBufferTimeOut) + " secs, dumping working set")
            print (self.Working)
            return (False,)
        