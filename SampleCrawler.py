'''
@Author: Rohan Achar ra.rohan@gmail.com
'''

from Crawler4py.Crawler import Crawler
from SampleConfig import SampleConfig

crawler = Crawler(SampleConfig())

print (crawler.StartCrawling())

exit(0)