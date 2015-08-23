from bs4 import BeautifulSoup
import urllib2
import re

# An entry on AutoTrader. Generally, it's an used car, but could be new too.
class ATEntry(object):
    
    # Constructor, maybe?
    def __init__(self, model, year, price):
        self.model = model
        self.year = year
        self.price = price
        
    def displayCsv(self):
        return "%s,%s,%s,%s" % (self.year, self.model, self.price, self.mileage)

# Scraper itself        
class ATScraper(object):

    # Constructor
    def __init__(self, make):
        self.make = make
        self.url = "http://www.autotrader.co.za/makemodel/make/%s/search?sort=PriceAsc&pageNumber=" % make
        print self.url
        
    
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
    
        # Need to do a bit of shuffling here for promoted/otherwise cars
        if(result.find("h2", "serpTitle") is not None):
            carName = result.find("h2", "serpTitle").string.strip()
        elif (result.find("h2", "serpTitleSma") is not None):
            carName = result.find("h2", "serpTitleSma").string.strip()
        else:
            carName = "Something went wrong here"
        
        carPrice = self.tryParseInt(result.find("div", "serpPrice").contents[0])
        carYear = self.tryParseInt(result.find("div", "serpAge").string)
    
        entry = ATEntry(carName, carYear, carPrice)
        
        specList = result.find("ul", "advertSpecs")
    
        specs = []
    
        mileage = -1
    
        for spec in specList.find_all("li"):
            specString = spec.string.strip()
            specs = specs + [specString]
            if specString.endswith("km"):
                mileage = self.tryParseInt(specString)
    
        entry.specs = specs 
        entry.mileage = mileage 
    
        return entry
    
    def scrapeEntries(self, page):
        content = urllib2.urlopen(self.url + page).read()
        soup = BeautifulSoup(content, "html5lib")
    
        entries = []
        for result in soup.find_all("div", "searchResult"): 
            entries = entries + [self.parseResult(result)]
        return entries