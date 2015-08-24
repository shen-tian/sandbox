from atscraper import ATScraper

make = "audi"
model = "a8"

scraper = ATScraper(make, model)

fileName = "%s-%s.csv" % (make, model)

target = open(fileName, "w")
    
entries = scraper.scrapeAllEntries(True)


for entry in entries:
    if len(entries) < 100:
        print entry.displayCsv()
    target.write(entry.displayCsv().encode("utf-8"))
    target.write("\n")
target.close()

print "Wrote output to %s" % fileName
    
