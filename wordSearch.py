#Import packages
import pandas as pd
import xlsxwriter as excel
import fitz
import re
import requests
import time
import glob
import pytesseract
from pdf2image import convert_from_path
import os

#Paths to:
data_url = "data/QC_Wells.csv"  #datafile
workbook_url = "H2SrelatedWells.xlsx" #filtered information stored in excel file

#Creating an excel file to store results
workbook = excel.Workbook(workbook_url)
worksheet = workbook.add_worksheet()

#Formating cells
headers_format = workbook.add_format({
    "bold":1,
    "border":2,
    "align":"center",

})
cell_format = workbook.add_format({
    "border":1,
    "align":"center"
})

#Creating the headers
#Column for the reports that mentions H2S
worksheet.merge_range("A1:B1", "H2S", headers_format)   
worksheet.write(1,0, "Well Number", headers_format)
worksheet.write(1,1, "Link to report", headers_format)

#Column for the reports that mentions methane or is work in progress
worksheet.merge_range("E1:F1", "Pending and Hydrocarbon Candidate", headers_format)
worksheet.write(1,4, "Well Number", headers_format)
worksheet.write(1,5, "Link to report", headers_format)

#Column for the reports that are images (to be checked if the imageToText function wasn't activated)
worksheet.merge_range("I1:J1", "Image Report", headers_format)
worksheet.write(1,8, "Well Number", headers_format)
worksheet.write(1,9, "Link to report", headers_format)

#Column for the reports that doesn't contain anything interesting 
worksheet.merge_range("M1:N1", "Nothing", headers_format)
worksheet.write(1,12, "Well Number", headers_format)
worksheet.write(1,13, "Link to report", headers_format)

#Column for the reports that cannot be ran with this program, need to be checked manually
worksheet.merge_range("Q1:R1", "Broken file", headers_format)
worksheet.write(1,16, "Well Number", headers_format)
worksheet.write(1,17, "Link to report", headers_format)


#load the data file in python
data = pd.read_csv(data_url)

#list of words to look for in the reports
wordList = ["H2S",
            "ulfure d'hydrogène", 
            "ulfite", 
            "ulfide", 

            ] 
wordlist2 = ["Travaux à réaliser",
            "ontamination d'Hydrocarbure",
            "ontamination d'hydrocarbure",
            "ontaminé aux hydrocarbures",
            "ontaminé aux Hydrocarbures",
            "ontamination en Hydrocarbure",
            "ontamination en hydrocarbure",
            "gaz acide",
            "gaz d'égout",
            "éthane",
            "Éthane",
            "ethane",
            "Ethane",
            "CH4",
            "C2H6",]
#there are 2 lists so that the reports that mentions H2S are categorized first

#Start the timer to see the runtime of the program
start = time.time()

def filterPDF():
    #storing the entries for the well number
    number = data["NO_ENTRE_1"] 
    #storing the entries for the links to the report
    pdfLinks = data["Link_to_inspection_report"]
    #variables for the rows of each column in the excel file
    rowH2S = 2
    rowMet = 2
    rowImg = 2
    rowNot =2
    rowError = 2
    #variable used to keep track of processing progress
    processedFile = 1

    for i in range(len(number)):
        #conditional to filter out the wells that have no links ("None" in the xlsx is consider as a float, while links are strings)
        if type(pdfLinks[i]) is not float:   
            #try and except to filter out broken files
            #conditionals used to write the number of the wells and their report link in the correct categories in the excel file
            try:
                #calling the function and storing the returned value in a variable that will be analyzed in the following lines
                result = wordSearch(pdfLinks[i], wordList, wordlist2)
                if result == "H2S":
                    worksheet.write(rowH2S,0, number[i], cell_format)
                    worksheet.write(rowH2S,1, pdfLinks[i], cell_format)
                    rowH2S+=1
                elif result == "Pending":
                    worksheet.write(rowMet,4, number[i], cell_format)   #implement the code here for image to text
                    worksheet.write(rowMet,5, pdfLinks[i], cell_format)
                    rowMet+=1
                elif result == "Image":
                    worksheet.write(rowImg,8, number[i], cell_format)   #implement the code here for image to text
                    worksheet.write(rowImg,9, pdfLinks[i], cell_format)
                    rowImg+=1

                elif result == "Nothing":
                    worksheet.write(rowNot,12, number[i], cell_format)
                    worksheet.write(rowNot,13, pdfLinks[i], cell_format)
                    rowNot+=1
                else:
                    worksheet.write(rowError,16, number[i], cell_format)
                    worksheet.write(rowError,17, pdfLinks[i], cell_format)
                    rowError+=1
            #if the file can't be opened by the fitz module, it will be writen under the broken file category in the excel file
            except fitz.fitz.FileDataError:
                    worksheet.write(rowError,16, number[i], cell_format)
                    worksheet.write(rowError,17, pdfLinks[i], cell_format)
                    rowError+=1
        i +=1
        #This tells us the number of files that have been processed so that we have an idea of the progression
        print(f"{processedFile}/{len(number)}")  
        processedFile+=1
    
def wordSearch(url, target: [str], target2: [str]):
    #gets the pdf from the web and stores it as a byte file
    #the while loop combined with the "timeout" attribute prevent the code to be stuck if a request takes too long
    #Instead, if the request didn't get anything after 6 seconds, python will raise a TimeoutError and will retry the request
    while True:
        try: 
            res = requests.get(url, timeout = 6)
            break
        except TimeoutError:
            continue
        #This exceptions is to catch cases where the url is broken and python cannot access it
        except requests.exceptions.ConnectionError:
            return("Broken") 
        
    #open the file as a pdf    
    reader = fitz.open(stream = res.content, filetype = "pdf")

    # get number of pages
    num_pages = reader.page_count  

    #assuming that the file isn't too big 
    #and also preventing any errors in the pdf format that would make the number of pages infinity, meaning that the code will loop forever
    if num_pages >100:     
        return "Too Large"

    #for each page of the pdf, run the searching code
    for i in range(num_pages):
        text = reader.load_page(i)
        text = text.get_text()

        #Assume that if the first page is an image, the whole report is in image format, so the function marks it as an image
        #If he page is blank, no strings, we consider it as an Image
        if text == "": 
            #Choose which one to use
            # Calling the function will take much longer, at least 4 times the runtime
            # For the present data, there is only a few reports that are useful so I toggled the simpler version on 
            return("Image")
            #return imageSearch(res, target, target2)  

        #for each word in the wordlist
        for j in range(len(target)):
            #Search the page and if it contains the target word
            res_search = re.search(target[j], text)
            #If the word is present, return a string that will classify it, else the code continues  
            if res_search is not None:
                return ("H2S")
            
    #same as above, only reason to have it duplicate is to search for the H2S related words first, so that they are in a separate column        
    for i in range(num_pages):
        text = reader.load_page(i)
        text = text.get_text()

        for k in range(len(target2)):
            res_search = re.search(target2[k], text)   
            if res_search is not None:
                return ("Pending")
    #after all the searches, if nothing was found, return a "nothing" string for the filter to classify it as not interesting
    return ("Nothing")


def imageSearch(path, target:[str], target2):
    #create a temporary pdf to store the content from the online pdf (like downloading a pdf)
    temp = "temp.pdf"
    with open(temp, "wb") as file:
        temporary_file = file.write(path.content)

    #get a path for the pdf in a list format containing other things
    pdfs = glob.glob(temp)


    for pdf_path in pdfs:
        #convert the pdf to a pillow image, image format supported by python
        pages = convert_from_path(pdf_path, 500)

        #iterate through each pages of the pdf one at the time
        for pageNum,imgBlob in enumerate(pages):
            #turn the image to strings through the tessearct OCR
            text = pytesseract.image_to_string(imgBlob,lang='eng')
            #search through the text like in the wordSearch function but before returning a value, the temporary pdf is deleted
            for j in range(len(target)):
                res_search = re.search(target[j], text)   #for each elements in the list "target", we do a word search by pattern matching in each page of the pdf
                if res_search is not None:
                    os.remove(temp)
                    return("H2S")
            for k in range(len(target2)):
                res_search = re.search(target2[k], text)   #for each elements in the list "target", we do a word search by pattern matching in each page of the pdf
                if res_search is not None:
                    os.remove(temp)
                    return ("Pending")

    os.remove(temp)
    return("Image")

def main():
    #calling the filter function
    filterPDF()
    #closing the excel workbook so that everything is saved
    workbook.close()
    #Get the time the code ended
    end = time.time()
    #Get the runtime by performing a substraction
    runtime = (end - start)/60
    #Print out the runtime to see how long it took to run the code
    print(f"Runtime: {runtime} minutes")   


if __name__ == "__main__":
    main()


