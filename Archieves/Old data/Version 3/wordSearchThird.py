#Import packages
import pandas as pd
import xlsxwriter as excel
import fitz
import re
import requests
import time

#Paths to the data file and the file where results are stored
data_url = "data/Wells(for practice).xlsx"
workbook_url = "H2SrelatedWells.xlsx"

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
worksheet.merge_range("A1:B1", "H2S Candidate", headers_format)
worksheet.write(1,0, "Well Number", headers_format)
worksheet.write(1,1, "Link to report", headers_format)

worksheet.merge_range("E1:F1", "Image Report", headers_format)
worksheet.write(1,4, "Well Number", headers_format)
worksheet.write(1,5, "Link to report", headers_format)

#New colomn so that further searched only need to iterate through these ones, since other ones are already confirmed or images, less to go through
worksheet.merge_range("I1:J1", "Nothing", headers_format)
worksheet.write(1,8, "Well Number", headers_format)
worksheet.write(1,9, "Link to report", headers_format)

worksheet.merge_range("M1:N1", "Broken file", headers_format)
worksheet.write(1,12, "Well Number", headers_format)
worksheet.write(1,13, "Link to report", headers_format)


#load the data file
data = pd.read_excel(data_url)
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
            "éthane"
            "Éthane"
            "ethane"
            "Ethane"
            "CH4"
            "C2H6"
              #all other variants
            ] 

start = time.time()

def filterPDF():
    number = data["Number"]
    pdfLinks = data["Link to inspection report"]
    rowH2S = 2
    rowImg = 2
    rowNot =2
    rowError = 2
    processedFile = 1

    for i in range(len(pdfLinks)):
        #conditional to filter out the wells that have no links ("None" in the xlsx is consider as a float, while links are strings)
        if type(pdfLinks[i]) is not float:   
            #try and except to filter out broken files
            #conditionals used to write the number of the wells and their report link in the correct categories in the excel file
            try:
                if wordSearch(pdfLinks[i], wordList) == "Present":
                    worksheet.write(rowH2S,0, number[i], cell_format)
                    worksheet.write(rowH2S,1, pdfLinks[i], cell_format)
                    rowH2S+=1
                elif wordSearch(pdfLinks[i], wordList) == "Image":
                    worksheet.write(rowImg,4, number[i], cell_format)   #implement the code here for image to text
                    worksheet.write(rowImg,5, pdfLinks[i], cell_format)
                    rowImg+=1
                elif wordSearch(pdfLinks[i], wordList) == "Too Large":
                    worksheet.write(rowError,12, number[i], cell_format)
                    worksheet.write(rowError,13, pdfLinks[i], cell_format)
                    rowError+=1
                else:
                    worksheet.write(rowNot,8, number[i], cell_format)
                    worksheet.write(rowNot,9, pdfLinks[i], cell_format)
                    rowNot+=1
            except fitz.fitz.FileDataError:
                    worksheet.write(rowError,12, number[i], cell_format)
                    worksheet.write(rowError,13, pdfLinks[i], cell_format)
                    rowError+=1
        i +=1
        print(f"{processedFile}/{len(number)}")  #This tells us the number of files that have been processed so that we have an idea of the progression
        processedFile+=1


def wordSearch(url, target: [str]):
    # open the pdf file
    res = requests.get(url)   #get the pdf from online and store in the variable as a bytes encoded file
    reader = fitz.open(stream = res.content, filetype = "pdf") #open the file as a pdf

    # get number of pages
    num_pages = reader.page_count  

    #assuming that the file isn't too big 
    #and also preventing any errors in the pdf format that would make the number of pages infinity, meaning that the code will loop forever
    if num_pages >100:     
        return "Too Large"

    # extract text and do the search 
    for i in range(num_pages):
        text = reader.load_page(i)
        text = text.get_text()
        if text == "":  #meaning that the page is blank == Image
            return("Image")  #Assume that if the first page is an image, the whole report is in image format, so the function marks it as an image
        for j in range(len(target)):
            res_search = re.search(target[j], text)   #for each elements in the list "target", we do a word search by pattern matching in each page of the pdf
            if res_search is not None:
                return ("Present")
            else:
                j+=1
    return ("Nothing")


def imageToText():
    ...       


def main():
    filterPDF()
    workbook.close()
    end = time.time()
    runtime = (end - start)/60
    print(f"Runtime: {runtime} minutes")   #to see how long it took to run the code

if __name__ == "__main__":
    main()


