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

data_url = "data\QC_Wells.csv"
workbook_url = "H2SrelatedWells.xlsx"

workbook = excel.Workbook(workbook_url)
worksheet = workbook.add_worksheet()

headers_format = workbook.add_format({
    "bold":1,
    "border":2,
    "align":"center",

})
cell_format = workbook.add_format({
    "border":1,
    "align":"center"
})

worksheet.merge_range("A1:B1", "H2S Candidate", headers_format)
worksheet.write(1,0, "Well Number", headers_format)
worksheet.write(1,1, "Link to report", headers_format)

worksheet.merge_range("E1:F1", "Image Report", headers_format)
worksheet.write(1,4, "Well Number", headers_format)
worksheet.write(1,5, "Link to report", headers_format)

worksheet.merge_range("I1:J1", "Nothing", headers_format)
worksheet.write(1,8, "Well Number", headers_format)
worksheet.write(1,9, "Link to report", headers_format)

worksheet.merge_range("M1:N1", "Broken file", headers_format)
worksheet.write(1,12, "Well Number", headers_format)
worksheet.write(1,13, "Link to report", headers_format)


data = pd.read_csv(data_url)
wordList = ["H2S",
            "ulfure d'hydrogène", 
            "ulfite", 
            "ulfide", 
            "ontamination d'Hydrocarbure",
            "ontaminé",
            "ydrocarbure"
            "gaz acide",
            "gaz d'égout"
            "thane"
            "CH4"
            "C2H6"
            ] 
number = data["NO_ENTRE_1"]
pdfLinks = data["Link_to_inspection_report"]
processedFile = 1
rowH2S = 2
rowImg = 2
rowNot =2
rowError = 2
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

def filterPDF(number, link):
    global rowH2S
    global rowImg
    global rowError
    global rowNot
    try:
        results = wordSearch(number, link, wordList)
        if results == "Present":
            worksheet.write(rowH2S,0, number, cell_format)
            worksheet.write(rowH2S,1, link, cell_format)
            rowH2S+=1
        elif results == "Image":
            worksheet.write(rowImg,4, number, cell_format)   
            worksheet.write(rowImg,5, link, cell_format)
            rowImg+=1
        elif results == "Problem":
            worksheet.write(rowError,12, number, cell_format)
            worksheet.write(rowError,13, link, cell_format)
            rowError+=1
        elif results == "Nothing":
            worksheet.write(rowNot,8, number, cell_format)
            worksheet.write(rowNot,9, link, cell_format)
            rowNot+=1
        else:
            return

    except fitz.fitz.FileDataError:
        worksheet.write(rowError,12, number, cell_format)
        worksheet.write(rowError,13, link, cell_format)
        rowError+=1
   
def wordSearch(number, url, target: [str]):

    result = timeLimit(url) 
    if result[0] == "Pass":
        runtimeTooLong.append({"number":number, "link":url})
        print("Passed")
        return
    elif result[0] == "Problem":
        return("Problem")
    else:
        res = result[1]


    reader = fitz.open(stream = res.content, filetype = "pdf") 

    num_pages = reader.page_count  

    if num_pages >100:     
        return "Problem"


    for i in range(num_pages):
        text = reader.load_page(i)
        text = text.get_text()
        if text == "":  
            return("Image")
            #return imageSearch(res, target) 
        for j in range(len(target)):
            res_search = re.search(target[j], text)   
            if res_search is not None:
                return ("Present")
            else:
                j+=1
    return ("Nothing")


def imageSearch(path, target:[str]):
    temp = "temp.pdf"
    with open(temp, "wb") as file:
        temporary_file = file.write(path.content)

    pdfs = glob.glob(temp)
    for pdf_path in pdfs:
        pages = convert_from_path(pdf_path, 500) 
        for pageNum,imgBlob in enumerate(pages):
            text = pytesseract.image_to_string(imgBlob,lang='eng')
            for j in range(len(target)):
                res_search = re.search(target[j], text)  
                if res_search is not None:
                    os.remove(temp)
                    return("Present")
                else:
                    j+=1
    os.remove(temp)
    return("Image")

def main():
    global processedFile
    for i in range(length):

        if type(pdfLinks[i]) is not float:   
           filterPDF(number[i], pdfLinks[i])
            
        else:
            print(f"{processedFile}/{len(number)}") 
            processedFile+=1

    while True:
        j = 0
        if runtimeTooLong == []:
            break
        else:
            for i in range(len(runtimeTooLong)):
                results =  timeLimit(pdfLinks[j]) 
                if results[0] != "Pass":
                    filterPDF(runtimeTooLong[j]["number"], runtimeTooLong[j]["link"])
                    runtimeTooLong.pop(j)
                    print(f"{processedFile}/{length}") 
                    processedFile+=1
                else:
                    j+=1
                    print("Passed")

    workbook.close()
    end = time.time()
    runtime = (end - start)/60
    print(f"Runtime: {runtime} minutes")  

if __name__ == "__main__":
    main()


