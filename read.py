import csv

rawData = []

with open('BMW.csv', 'rb') as f:
    reader = csv.reader(f,delimiter =";")
    for row in reader:
        rawData = rawData + [row]
        
print "Raw data: %s entries" % len(rawData)

clnData = []

for i in rawData:
  if i not in clnData:
    clnData.append(i)
    
print "Dedup data: %s entries" % len(clnData)

wordList = {}
tokenCount = 0

for line in clnData:
	tokens = str.split(line[1])
	for token in tokens:
		if token in wordList:
			wordList[token] = wordList[token] + 1
		else:
			wordList[token] = 1
	tokenCount = tokenCount + len(tokens)
			
print "Total tokens %s" % tokenCount

for x in sorted(wordList, key=wordList.get, reverse=True)[:20]:
	print "%s %s" % (wordList[x], x)
	
#do some specific data dump

ofile  = open('320i.csv', "wb")
writer = csv.writer(ofile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)

for car in clnData:
	if "320i" in str.split(car[1]):
		writer.writerow(car)

ofile.close() 