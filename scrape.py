from atscraper import ATScraper
import argparse
import logging
import datetime

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

#logging.basicConfig(level=logging.INFO)

handler = logging.FileHandler('scrape-%s.log' % datetime.datetime.now().strftime("%Y%m%d-%H%M"))
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)

s_handler = logging.StreamHandler()
s_handler.setLevel(logging.INFO)
s_handler.setFormatter(formatter)

logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(handler)
logging.getLogger().addHandler(s_handler)

fileName = "%s-%s.csv" % (make, model)

if make == "":
    fileName = "all.csv"

target = open(fileName, "w")
    
entries = scraper.scrape_all_entries()

for entry in entries:
    target.write(entry.display_csv().encode("utf-8"))
    target.write("\n")
target.close()

#logger.info("Wrote output to %s" % fileName)
    
