from atscraper import ATScraper

firstPage = 1
lastPage = 3

scraper = ATScraper("suzuki", "jimny")

target = open("foo.csv", "w")
lastPage = scraper.getNumberOfPages()
print "there are %s pages" % lastPage

for pageNum in range(firstPage, lastPage + 1):
    print "pulling page %s" % pageNum
    
    entries = scraper.scrapeEntries(str(pageNum))

    for entry in entries:
        print entry.displayCsv()
        target.write(entry.displayCsv().encode("utf-8"))
        target.write("\n")
target.close()
    
