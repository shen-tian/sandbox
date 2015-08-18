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

# Try to make an int. Failing that, -1
def tryParseInt(str):
	try:
		cleaned = re.sub("[^0-9]", "", str)
		return int(cleaned)
	except ValueError:
		return -1

# Takes a searchResult tag from a page and scrapes it for info.
def parseResult(result):
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
   		
   	carPrice = tryParseInt(result.find("div", "serpPrice").contents[0])
   	carYear = tryParseInt(result.find("div", "serpAge").string)
   	
   	entry = ATEntry(carName, carYear, carPrice)
   	   	
   	specList = result.find("ul", "advertSpecs")
   	
   	specs = []
   	
   	mileage = -1
   	
   	for spec in specList.find_all("li"):
   		specString = spec.string.strip()
   		specs = specs + [specString]
   		if specString.endswith("km"):
   			mileage = tryParseInt(specString)
   	
   	entry.specs = specs 
   	entry.mileage = mileage 
   	
   	return entry
   	
def scrapeEntries(url):
	content = urllib2.urlopen(url).read()
	soup = BeautifulSoup(content, "html5lib")
	
	entries = []
	for result in soup.find_all("div", "searchResult"): 
		entries = entries + [parseResult(result)]
	return entries
   	
# Main program

baseAllUrl = "http://www.autotrader.co.za/search?sort=PriceAsc&pageNumber="
baseBmwUrl = "http://www.autotrader.co.za/makemodel/make/bmw/search?sort=PriceAsc&pageNumber="
baseCptUlr = "http://www.autotrader.co.za/radius/200km/search?sort=PriceAsc&county=Western+Cape&longitude=18.42322&locationName=Cape+Town&latitude=-33.92584&pageNumber="
baseAlfaUlr = "http://www.autotrader.co.za/makemodel/make/ALFA%20ROMEO/search?sort=PriceAsc&pageNumber="

url = baseAlfaUlr
firstPage = 1
lastPage = 13


target = open("foo.csv", "w")

for pageNum in range(firstPage, lastPage):
	print "pulling page %s" % pageNum
	
	entries = scrapeEntries(url + str(pageNum))

	for entry in entries:
		target.write(entry.displayCsv().encode("utf-8"))
		target.write("\n")

target.close()
	
