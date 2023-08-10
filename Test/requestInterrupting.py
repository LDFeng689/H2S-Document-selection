import pandas as pd
import requests
import time

data_url = "data\QC_Wells.csv"
data = pd.read_csv(data_url)
number = data["NO_ENTRE_1"]
pdfLinks = data["Link_to_inspection_report"]
processedFile = 1
runtimeTooLong = []
length = len(number)
start = time.time()

def timeLimit(url):
    try:
        res = requests.get(url, timeout = 6)
        return("Good", res)
    except TimeoutError:
        return("Pass")
    except requests.exceptions.ConnectionError:
        return("Problem", "Broken")

for i in range(length):
    if type(pdfLinks[i]) is not float:
        results =  timeLimit(pdfLinks[i])
        if results[0] == "Pass":
            runtimeTooLong.append({"number":number[i], "link":pdfLinks[i]})
            print("Passed")
        else:
            res = results[1]
            print(f"{processedFile}/{length}") 
            processedFile+=1
    print(f"{processedFile}/{length}") 
    processedFile+=1


while True:
    j = 0
    if runtimeTooLong == []:
        break
    else:
        for i in range(len(runtimeTooLong)):
            results =  timeLimit(pdfLinks[j]) 
            if results[0] != "Pass":
                runtimeTooLong.pop(j)
                print(f"{processedFile}/{length}") 
                processedFile+=1
            else:
                j+=1
                print("Passed")
end = time.time()
runtime = (end - start)/60
print(f"Runtime: {runtime} minutes")  
