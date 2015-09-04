from bs4 import BeautifulSoup
import re
import requesocks
import time
import logging
import traceback

# An entry on AutoTrader. Generally, it's an used car, but could be new too.
class ATEntry(object):

    # Constructor. Needs 
    def __init__(self, model, year, price, mileage, url):
        self.model = model
        self.year = year
        self.price = price
        self.mileage = mileage
        self.url = url
        
    def display_csv(self):
        return "%s\t%s\t%s\t%s\t%s" % \
            (self.year, self.model, self.price, self.mileage, self.url)

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
        
        self.logger = logging.getLogger(__name__)
            
    def makeSession(self):
        self.session = requesocks.session()
        #Use Tor for both HTTP and HTTPS
        if self.tor:
            self.session.proxies = {'http': 'socks5://localhost:9150', 
            'https': 'socks5://localhost:9150'}
        
            
    # Try to make an int. Failing that, -1
    def try_parse_int(self, str):
        try:
            cleaned = re.sub("[^0-9]", "", str)
            return int(cleaned)
        except ValueError:
            return -1
    
    # Takes a searchResult tag from a page and scrapes it for info.
    def parse_result(self, result):
        car_name = ""
        car_year = -1
        car_price = -1
        specs = []
        mileage = -1
        new = False
        url = ""
            
        # This portion is different for the three classes 
        # (newCar, featureRes, and standard)
        if "newCar" in result["class"]:
            car_name = result.find("div", "resultHeader").find("h2").string.strip()
            url = result.find("div", "resultHeader").find("h2").find("a")["href"]
            year_portion = car_name[:4]
            car_year = self.try_parse_int(year_portion)
            car_name = car_name[4:].strip()
            new = True
        else:
            if "featureRes" in result["class"]:
                car_name = result.find("h2", "serpTitleSma").string.strip()
                url = result.find("h2", "serpTitleSma").find("a")["href"]
            else:
                car_name = result.find("h2", "serpTitle").string.strip()
                url = result.find("h2", "serpTitle").find("a")["href"]
            car_year = self.try_parse_int(result.find("div", "serpAge").string)
        
        # Cleaning the URL
        trailing_bits = url.find("/makemodel")
        if trailing_bits != -1:
            url = url[:trailing_bits]            
        
        # This is the same for all three classes
        car_price = self.try_parse_int(result.find("div", "serpPrice").contents[0])
    
        for spec in result.find("ul", "advertSpecs").find_all("li"):
            spec_string = spec.string.strip()
            specs = specs + [spec_string]
            if spec_string.endswith("km"):
                mileage = self.try_parse_int(spec_string)
    
        entry = ATEntry(car_name, car_year, car_price, mileage, url)
    
        entry.new = new
        entry.specs = specs
          
        return entry
    
    # Go through all entries
    def scrape_all_entries(self):
        entries = []
        num_of_pages = self.get_number_of_pages()
        self.logger.info("There are %s pages" % num_of_pages)
        for page_num in range(1, num_of_pages + 1):    
            new_entries = self.scrape_entries(str(page_num))
            entries = entries + new_entries
        return entries
    
    # Go through all entries on the page
    def scrape_entries(self, page):
        self.logger.info("Downloading page %s" % page)
        try:
            response = self.session.get(self.url + page, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")
        except Exception:
            self.logger.warn("Timeout for page %s" % page)
            time.sleep(1)
            self.makeSession()
            return self.scrape_entries(page)
            
        entries = []
        for result in soup.find_all("div", "searchResult"): 
            try:
                entry = self.parse_result(result)
                entries = entries + [entry]
            except:
                self.logger.warn("Error parsing entry on page %s" % page)
                self.logger.debug(traceback.format_exc())
                self.logger.debug(result.contents)
        return entries
        
    # Gives number of pages for this query
    def get_number_of_pages(self):
        response = self.session.get(self.url + "1")
        content = response.text
        soup = BeautifulSoup(content, "html.parser")
        
        last_page_link = soup.find("ol", "paginator").find("a", "last")
        if last_page_link is not None:
            url = last_page_link["href"]
            return self.try_parse_int(url[url.rfind("=")+1:])
        else:
            return 1