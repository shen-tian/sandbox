from atscraper import ATScraper
import argparse

parser = argparse.ArgumentParser(description='Scraper for autotrader.co.za')

parser.add_argument('--make', action="store", dest="make", default="", 
                    help="Make to search for, e.g. honda")
parser.add_argument('--model', action="store", dest="model", default="",
                    help="Model to search for, e.g. civic")
parser.add_argument('--tor', action="store_true", default=False,
                    help="Wheher to connect via the Tor SOCKS proxy")
                    
result = parser.parse_args()

make = result.make
model =  result.model

scraper = ATScraper(make, model, result.tor)

fileName = "%s-%s.csv" % (make, model)

if make == "":
    fileName = "all.csv"

target = open(fileName, "w")
    
entries = scraper.scrapeAllEntries()

for entry in entries:
    if len(entries) < 100:
        print entry.displayCsv()
    target.write(entry.displayCsv().encode("utf-8"))
    target.write("\n")
target.close()

print "Wrote output to %s" % fileName
    
