import numpy as np
import statsmodels.api as sm
import csv

y = [1,2,3,4,3,4,5,4,5,5,4,5,4,5,4,5,6,5,4,5,4,3,4]

x = [
     [4,2,3,4,5,4,5,6,7,4,8,9,8,8,6,6,5,5,5,5,5,5,5],
     #[4,1,2,3,4,5,6,7,5,8,7,8,7,8,7,8,7,7,7,7,7,6,5],
     [4,1,2,5,6,7,8,9,7,8,7,8,7,7,7,7,7,7,6,6,4,4,4]
     ]

def reg_m(y, x):
    ones = np.ones(len(x[0]))
    X = sm.add_constant(np.column_stack((x[0], ones)))
    for ele in x[1:]:
        X = sm.add_constant(np.column_stack((ele, X)))
    results = sm.OLS(y, X).fit()
    return results
    
rawData = []

with open('320i.csv', 'rb') as f:
    reader = csv.reader(f,delimiter =";")
    for row in reader:
        rawData = rawData + [row]
        
print "Raw data: %s entries" % len(rawData)

clnData = []
price = []
year = []
mileage = []

for i in rawData:
  if i not in clnData:
  	clnData.append(i)
  	price.append(int(i[2]))
  	year.append(int(i[0]))
  	mileage.append(int(i[3]))
    
print "Dedup data: %s entries" % len(price)
    
print reg_m(price , [year]).summary()