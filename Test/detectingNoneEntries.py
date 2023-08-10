#Used to detect how a None Entry in the report table looks like in a Python environment
#The results are that they are of type "float"
#this allows the implementation of a conidtional to ignore the wells that have no reports linked to them

import pandas as pd

data_url = "Wells(for practice).xlsx"
data = pd.read_excel(data_url)
 
number = data["Number"]
pdf = data["Link to inspection report"]

none = 0
index = 0

for i in range(len(pdf)):
    if type(pdf[i]) is float:
        print("none")
        none+=1
    else:
        print(pdf[i])
        index+=1

print(index)
print(none)