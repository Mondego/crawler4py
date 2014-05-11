'''
@Author: Rohan Achar ra.rohan@gmail.com
'''

import time

from threading import *

from Crawler4py import UrlManager, Fetcher

class Crawler:
    def __init__(self, config):
        config.ValidateConfig()
        self.config = config
        self.urlManager = UrlManager.UrlManager(config)
        self.fetcher = Fetcher.Fetcher(config)
        self.freeworkers = set(range(self.config.MaxWorkerThreads))
        self.busyworkers = set()
        self.workersLock = Lock()
        self.workersDict = {}
        

    def StartCrawling(self):
        print ("Timestamp of start: " + time.strftime("%c"))
        outputWriter = Thread(target = self.__WriteDataOut, args = ())
        outputWriter.start()
        try:
            workerTry = self.__GetFreeWorker()
            while workerTry[0]:
                urlTry = None
                retryCount = 0
                while True:
                    urlTry = self.urlManager.GetFromFrontier()
                    if urlTry[0]:
                        break

                    time.sleep(0.1)
                    retryCount += 1
                    if (retryCount >= self.config.FrontierTimeOut / 0.1):
                        return "Exit, No More urls in Frontier"

                workerThread = Thread(target = self.__StartWorker, args = (workerTry[1], urlTry[1], urlTry[2]))
                self.workersDict[workerTry[1]] = workerThread
                workerThread.start()
                time.sleep(self.config.PolitenessDelay/1000)
                workerTry = self.__GetFreeWorker()

            print ("Waiting for Output buffer to clear")
            outputWriter.join()
            print ("Waiting for all threads to end." )
            print ("Timestamp of message: " + time.strftime("%c"))
            print ("Please close manually if next message doesnt appear for long time")

            for key in range(self.config.MaxWorkerThreads):
                if key in self.workersDict:
                    self.workersDict[key].join()
        
        except KeyboardInterrupt:
            print ("Exitting, Waiting for Output buffer to clear so that data is not lost")
            outputWriter.join()


        print ("All Threads cleared")
        return "Crawler Exiting"

    
    def __GetFreeWorker(self):
        retryCount = 0
        while True:
            if len(self.freeworkers) > 0:
                with self.workersLock:
                    return True, self.freeworkers.pop()

            time.sleep(0.1)
            retryCount += 1
            if (retryCount >= self.config.WorkerTimeOut / 0.1):
                return False, None

    def __StartWorker(self, id, url, depth):
        with self.workersLock:
            self.busyworkers.add(id)

        try:
            self.fetcher.FetchUrl(url, depth, self.urlManager)
            self.urlManager.MarkUrlAsDone(url)
        finally:
            with self.workersLock:
                self.busyworkers.remove(id)
                del self.workersDict[id]
                self.freeworkers.add(id)
            
        return

    def __WriteDataOut(self):
        dataTry = self.urlManager.GetOutput()
        while dataTry[0]:
            self.config.HandleData(dataTry[1])
            dataTry = self.urlManager.GetOutput()

