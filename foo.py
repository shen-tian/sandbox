from atscraper import ATScraper

firstPage = 1
lastPage = 60

scraper = ATScraper("suzuki")

target = open("foo.csv", "w")

for pageNum in range(firstPage, lastPage):
    print "pulling page %s" % pageNum
    
    entries = scraper.scrapeEntries(str(pageNum))

    for entry in entries:
        print entry.displayCsv()
        target.write(entry.displayCsv().encode("utf-8"))
        target.write("\n")
target.close()
    
