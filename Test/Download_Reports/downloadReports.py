import pandas as pd
import requests
import fitz

data_url = "data/Wells(for practice).xlsx"
#load the data file
data = pd.read_excel(data_url)

number = data["Number"]
pdfLinks = data["Link to inspection report"]


for i in range(len(number)):
    if type(pdfLinks[i]) is not float: #conditional to filter out the wells that have no links ("None" in the xlsx is consider as a float, while links are strings)
        try:
            res = requests.get(pdfLinks[i], stream = True)
            with open(f"Download_Reports/All_Reports/{number[i]}.pdf", "wb") as file:
                PDFbyte = file.write(res.content)
        except fitz.fitz.FileDataError:
            print(f"Number {number[i]}'s file is broken.")

