import csv
import logging.config
import os
import datetime
import traceback
import json

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
        
    def has_word(self, word):
        for token in self.tokens:
            if token[0] == word: 
                return token[1] is ""
                
        return False
        

# The classification engine
class CarClassifier(object):

    # Constructor.
    # file_name is file with classification data
    def __init__(self, file_name):
    
        with open(file_name) as data_file:    
            data = json.load(data_file)
        
        self.known_makes = data["makes"]
        self.known_models = data["models"]
        self.known_misc = data["misc"]
        
    def guess_by_string(self, name_string):
        result = {}
        
        words = str.split(name_string.lower())
        
        # Check if we can directly identify make
        for word in words:
            if word in self.known_makes:
                result["make"] = {(word, 1)}
        
        # Check if we can directly identify model
        for word in words:
            if word in self.known_models:
                result["model"] = {(word, 1)}
        
        return result
        
    def infer(self, car_entry):
        self.infer_make(car_entry)
        self.infer_model(car_entry)
        self.infer_prop(car_entry, self.known_misc, "misc")
    
    def infer_prop(self, car_entry, known_values, meta_tag):
        return_val = ""
        
        for token in car_entry.tokens:
            if token[0] in known_values:
                token[1] = meta_tag
                return_val = token[0]
        
        for index in range(0, len(car_entry.tokens) - 2):
            double_token = car_entry.tokens[index][0] + " " + \
                car_entry.tokens[index + 1][0]
            if double_token in known_values:
                car_entry.tokens[index][1] = meta_tag
                car_entry.tokens[index + 1][1] = meta_tag
                return_val = double_token
        
        return return_val
    
    
    def infer_make(self, car_entry):
        car_entry.make = self.infer_prop(car_entry, self.known_makes, "make")
    
    def infer_model(self, car_entry):
        car_entry.model = self.infer_prop(car_entry, self.known_models, "model")

# Logging setup 
def setup_logging(default_path='logging.json', default_level=logging.INFO):
        path = default_path
        if os.path.exists(path):
            with open(path, 'rt') as f:
                config = json.load(f)
            logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=default_level)
# Main

file_name = "sep-all.csv"
min_year = 2005

# Logging shit

setup_logging()
logger = logging.getLogger()

# Initialise the classification engine

classifier = CarClassifier("cardata.json")

# Read input

logger.info("Reading input")

raw_data = []
with open(file_name, 'rb') as f:
    reader = csv.reader(f, delimiter =",")
    for row in reader:
        raw_data.append(row)

# Filter

logger.info("Filtering data")

hashes = {}
entries = []

for row in raw_data:
    try:
        year = int(row[0])
        price = int(row[2])
        mileage = int(row[3])
    
        row_as_string = row[0] + row[1] + row[2] + row[3]
        
        if (row_as_string not in hashes) and (year > min_year) and (price > 1):
            hashes[row_as_string] = 1
            entries.append(CarEntry(row[1], year, price, mileage))
    except:
        logger.debug("Parsing error with %s" % row[1])
        logger.debug(traceback.format_exc())

logger.info("Starting with %s entries. filtered down to %s" % (len(raw_data), len(entries)))

unknown_wordlist = {}
identified_models = {}

make_infered = 0
model_infered = 0

# Try to classify everything

logger.info("Classifying")

for entry in entries:
    classifier.infer(entry)
    if entry.know_make():
        make_infered += 1
    if entry.know_model():
        model_infered += 1
        model_str = "%s :: %s" % (entry.make, entry.model)
        if model_str in identified_models:
            identified_models[model_str] += 1
        else:
            identified_models[model_str] = 1
    for token in entry.tokens:
        if token[1] is "":
            word = token[0]
            if word in unknown_wordlist:
                unknown_wordlist[word] += 1
            else:
                unknown_wordlist[word] = 1
# Report on success
logger.info("Infered %s makes and %s models" % (make_infered, model_infered))

# Report on outstanding tokens

logger.info("Unrecognised tokens")

for word in sorted(unknown_wordlist, key=unknown_wordlist.get, reverse=True)[:200]:
    rlu_make = {}
    rlu_model = {}
    
    has_make = 0
    has_model = 0
    match = 0
    
    for entry in entries:
        if entry.has_word(word):
            match += 1
            if entry.know_make():
                has_make += 1
                if entry.make in rlu_make:
                    rlu_make[entry.make] += 1
                else:
                    rlu_make[entry.make] = 1
            if entry.know_model():
                has_model += 1
                if entry.model in rlu_model:
                    rlu_model[entry.model] += 1
                else:
                    rlu_model[entry.model] = 1
    
    if has_model / float(match) > .1:
        #print "sub"
        continue 
    elif has_make / float(match) > .9 and has_model / float(match) < .1:
        print "model"
    elif has_make / float(match) < .1:
        print "make"
    breakdown_str = ""
    for make in rlu_make:
        percentage = rlu_make[make]/float(unknown_wordlist[word])
        if percentage > 0.05:
            breakdown_str = breakdown_str + "%s:%.2f " % (make, percentage)
    breakdown_str = breakdown_str + "## "
    for model in rlu_model:
        percentage = rlu_model[model]/float(unknown_wordlist[word])
        if percentage > 0.05:
            breakdown_str = breakdown_str + "%s:%.2f " % (model, percentage)
    logger.info("%5s %-10s %s" % (unknown_wordlist[word], word, breakdown_str))

#for entry in entries[10000:10010]:
#    print "%s#%s" % (entry.description, classifier.guess_by_string(entry.description))