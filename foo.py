from atscraper import ATScraper

make = ""
model = ""

scraper = ATScraper(make, model, True)

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
    
