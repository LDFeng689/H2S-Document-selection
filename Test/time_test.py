#Used to test the time used to filter 1 report

#Import packages
import pandas as pd
import xlsxwriter as excel
import fitz
import re
import requests
import time

#Just too see more of the data during tests
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

#Paths to the data file and the file where results are stored
data_url = "https://sigpeg.mrn.gouv.qc.ca/rapport/B198_insp_inactif_2019-06-06_Publique.pdf"
#list of words to look for, related to H2S
wordList = ["H2S",
            "ulfure d'hydrogène", 
            "ulfite", 
            "ulfide", 
            "h2s", 
            "ontamination d'Hydrocarbure",
            "ontamination d'hydrocarbure",
            "ontaminé aux hydrocarbures",
            "ontaminé aux Hydrocarbures",
            "ontamination en Hydrocarbure",
            "ontamination en hydrocarbure",
            "gaz acide",
            "gaz d'égout"
              #all other variants
            ] 
start = time.time()
def filterPDF(url):


    if type(url) is not float:      #conditional to filter out the wells that have no links ("None" in the xlsx is consider as a float, while links are strings)
            if wordSearch(data_url, wordList) == "Present":
               print("present")
            elif wordSearch(data_url, wordList) == "Image":
                print("Image")
            else:
                print("Nothing")

def wordSearch(url, target: [str]):
        # open the pdf file from online
    res = requests.get(url)
    reader = fitz.open(stream = res.content, filetype = "pdf")

    #reader = fitz.open(url) #from disk

    # get number of pages
    num_pages = reader.page_count

    # extract text and do the search 
    for i in range(num_pages):
        text = reader.load_page(i)
        text = text.get_text()
        if text == "":  #meaning that the page is blank == Image
            return("Image")
        for i in range(len(target)):
            res_search = re.search(target[i], text)
            if res_search is not None:
                return ("Present")
            else:
                i+=1
    return ("Nothing")
    


if __name__ == "__main__":
    filterPDF(data_url)
    end = time.time()
    duration = (end - start)/60
    print(f"It took {duration} minutes to run.")
    