from atscraper import ATScraper

scraper = ATScraper("mazda", "rx8")

target = open("foo.csv", "w")
    
entries = scraper.scrapeAllEntries()

for entry in entries:
    print entry.displayCsv()
    target.write(entry.displayCsv().encode("utf-8"))
    target.write("\n")
target.close()
    
