from bs4 import BeautifulSoup
import urllib2
import re
import requesocks
import time

# An entry on AutoTrader. Generally, it's an used car, but could be new too.
class ATEntry(object):
    
    # Constructor
    def __init__(self, model, year, price):
        self.model = model
        self.year = year
        self.price = price
        
    def displayCsv(self):
        return "%s,%s,%s,%s" % (self.year, self.model, self.price, self.mileage)

# Scraper itself        
class ATScraper(object):

    # Constructor
    def __init__(self, make="", model="", tor=False):
        filterString = ""
        
        self.make = make
        if make is not "":
            filterString = filterString + "/makemodel/make/%s" % make
        
        self.model = model
        if model is not "":
            filterString = filterString + "/model/%s" % model
            
        self.url = "http://www.autotrader.co.za%s" \
        "/search?sort=PriceAsc&pageNumber=" % filterString
        self.tor = tor
        
        self.makeSession()
            
    def makeSession(self):
        self.session = requesocks.session()
        #Use Tor for both HTTP and HTTPS
        if self.tor:
            self.session.proxies = {'http': 'socks5://localhost:9150', 
            'https': 'socks5://localhost:9150'}
        
            
    # Try to make an int. Failing that, -1
    def tryParseInt(self, str):
        try:
            cleaned = re.sub("[^0-9]", "", str)
            return int(cleaned)
        except ValueError:
            return -1
    
    # Takes a searchResult tag from a page and scrapes it for info.
    def parseResult(self, result):
        carName = ""
        carYear = -1
        carPrice = -1
        specs = []
        mileage = -1
        new = False
            
        # This portion is different for the three classes 
        # (newCar, featureRes, and standard)
        if "newCar" in result["class"]:
            carName = result.find("div", "resultHeader").find("h2").string.strip()
            yearPortion = carName[:4]
            carYear = self.tryParseInt(yearPortion)
            carName = carName[4:].strip()
            new = True
        else:
            if "featureRes" in result["class"]:
                carName = result.find("h2", "serpTitleSma").string.strip()
            else:
                carName = result.find("h2", "serpTitle").string.strip()
            carYear = self.tryParseInt(result.find("div", "serpAge").string)
        
        # This is the same for all three classes
        carPrice = self.tryParseInt(result.find("div", "serpPrice").contents[0])
    
        entry = ATEntry(carName, carYear, carPrice)
    
        for spec in result.find("ul", "advertSpecs").find_all("li"):
            specString = spec.string.strip()
            specs = specs + [specString]
            if specString.endswith("km"):
                mileage = self.tryParseInt(specString)
    
        entry.specs = specs 
        entry.mileage = mileage 
        entry.new = new
    
        return entry
    
    # Go through all entries
    def scrapeAllEntries(self):
        entries = []
        numOfPages = self.getNumberOfPages()
        print "there are %s pages" % numOfPages
        for pageNum in range(1, numOfPages + 1):    
            newEntries = self.scrapeEntries(str(pageNum))
            entries = entries + newEntries
        return entries
    
    # Go through all entries on the page
    # @profile
    def scrapeEntries(self, page):
        print "pulling page %s" % page
        try:
            response = self.session.get(self.url + page, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")
        except Exception:
            print "Timeout for page %s" % page
            time.sleep(1)
            self.makeSession()
            return self.scrapeEntries(page)
        entries = []
        for result in soup.find_all("div", "searchResult"): 
            entries = entries + [self.parseResult(result)]
        return entries
        
    # Gives number of pages for this query
    def getNumberOfPages(self):
        response = self.session.get(self.url + "1")
        content = response.text
        soup = BeautifulSoup(content, "html5lib")
        
        lastPageLink = soup.find("ol", "paginator").find("a", "last")
        if lastPageLink is not None:
            url = lastPageLink["href"]
            return self.tryParseInt(url[url.rfind("=")+1:])
        else:
            return 1