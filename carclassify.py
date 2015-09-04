import csv

# A raw entry, to be classified. 
class CarEntry(object):
    
    # Constructor
    def __init__(self, description, year, price, mileage):
        self.description = description.lower()
        self.year = year
        self.price = price
        self.mileage = mileage
        
        self.make = ""
        self.model = ""
        self.submodel = ""
        
        bits = str.split(self.description)
        self.tokens = []
        for bit in bits:
            self.tokens.append([bit,""])
        
    def know_make(self):
        return self.make != ""
        
    def know_model(self):
        return self.model != ""
        

# The classification engine
class CarClassifier(object):

    # Constructor.
    # file_name is file with classification data
    def __init__(self, file_name):
        self.known_makes = ("honda",)
        self.known_models = ("ballade", "civic", "jazz")
        
    def infer_make(self, car_entry):
        for token in car_entry.tokens:
            if token[0] in self.known_makes:
                token[1] = "make"
                car_entry.make = token[0]
    
    def infer_model(self, car_entry):
        for token in car_entry.tokens:
            if token[0] in self.known_models:
                token[1] = "model"
                car_entry.model = token[0]
        
# Main

file_name = "honda-.csv"
min_year = 2010


# Initialise the classification engine

classifier = CarClassifier("cardata.json")

# Read input

raw_data = []
with open(file_name, 'rb') as f:
    reader = csv.reader(f,delimiter ="\t")
    for row in reader:
        raw_data = raw_data + [row]

# Filter

clean_data = []
entries = []

for row in raw_data:
    year = int(row[0])
    price = int(row[2])
    mileage = int(row[3])
    
    if (row not in clean_data) and (year > min_year) and (price > 1):
        clean_data.append(row)
        entries.append(CarEntry(row[1], year, price, mileage))

print "Starting with %s entries. filtered down to %s" % (len(raw_data), len(clean_data))

# Try to classify everything

unknown_wordlist = {}

make_infered = 0
model_infered = 0

for entry in entries:
    classifier.infer_make(entry)
    classifier.infer_model(entry)
    if entry.know_make():
        make_infered += 1
    if entry.know_model():
        model_infered += 1
    for token in entry.tokens:
        if token[1] is "":
            word = token[0]
            if word in unknown_wordlist:
                unknown_wordlist[word] += 1
            else:
                unknown_wordlist[word] = 1
        

# Report on success

print "Infered %s makes and %s models" % (make_infered, model_infered)

# Report on outstanding tokens

print "Unrecognised tokens"

for x in sorted(unknown_wordlist, key=unknown_wordlist.get, reverse=True)[:20]:
	print "%5s %s" % (unknown_wordlist[x], x)