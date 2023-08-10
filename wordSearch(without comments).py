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

data_url = "data/QC_Wells.csv"
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
worksheet.merge_range("A1:B1", "H2S", headers_format)
worksheet.write(1,0, "Well Number", headers_format)
worksheet.write(1,1, "Link to report", headers_format)

worksheet.merge_range("E1:F1", "Pending and Hydrocarbon Candidate", headers_format)
worksheet.write(1,4, "Well Number", headers_format)
worksheet.write(1,5, "Link to report", headers_format)

worksheet.merge_range("I1:J1", "Image Report", headers_format)
worksheet.write(1,8, "Well Number", headers_format)
worksheet.write(1,9, "Link to report", headers_format)

worksheet.merge_range("M1:N1", "Nothing", headers_format)
worksheet.write(1,12, "Well Number", headers_format)
worksheet.write(1,13, "Link to report", headers_format)

worksheet.merge_range("Q1:R1", "Broken file", headers_format)
worksheet.write(1,16, "Well Number", headers_format)
worksheet.write(1,17, "Link to report", headers_format)


data = pd.read_csv(data_url)
wordList = ["H2S",
            "ulfure d'hydrogène", 
            "ulfite", 
            "ulfide" 
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
            "C2H6",
]

start = time.time()

def filterPDF():
    number = data["NO_ENTRE_1"]
    pdfLinks = data["Link_to_inspection_report"]
    rowH2S = 2
    rowMet = 2
    rowImg = 2
    rowNot =2
    rowError = 2
    processedFile = 1

    for i in range(len(pdfLinks)):
        if type(pdfLinks[i]) is not float:   
            try:
                result = wordSearch(pdfLinks[i], wordList, wordlist2)
                if result == "H2S":
                    worksheet.write(rowH2S,0, number[i], cell_format)
                    worksheet.write(rowH2S,1, pdfLinks[i], cell_format)
                    rowH2S+=1
                elif result == "Pending":
                    worksheet.write(rowMet,4, number[i], cell_format)   
                    worksheet.write(rowMet,5, pdfLinks[i], cell_format)
                    rowMet+=1
                elif result == "Image":
                    worksheet.write(rowImg,8, number[i], cell_format)   
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

            except fitz.fitz.FileDataError:
                    worksheet.write(rowError,16, number[i], cell_format)
                    worksheet.write(rowError,17, pdfLinks[i], cell_format)
                    rowError+=1
        i +=1
        print(f"{processedFile}/{len(number)}")  
        processedFile+=1
    
def wordSearch(url, target: [str], target2: [str]):

    while True:
        try: 
            res = requests.get(url, timeout = 6)
            break
        except TimeoutError:
            continue
        except requests.exceptions.ConnectionError:
            return("Broken") 
    reader = fitz.open(stream = res.content, filetype = "pdf") 

    num_pages = reader.page_count  

   
    if num_pages >100:     
        return "Too Large"


    for i in range(num_pages):
        text = reader.load_page(i)
        text = text.get_text()
        if text == "": 
            return("Image")
            #return imageSearch(res, target, target2)  
        for j in range(len(target)):
            res_search = re.search(target[j], text)   
            if res_search is not None:
                return ("H2S")
            
    for i in range(num_pages):
        text = reader.load_page(i)
        text = text.get_text()

        for k in range(len(target2)):
            res_search = re.search(target2[k], text)   
            if res_search is not None:
                return ("Pending")

    return ("Nothing")


def imageSearch(path, target:[str], target2):
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
                    return("H2S")
            for k in range(len(target2)):
                res_search = re.search(target2[k], text)   
                if res_search is not None:
                    os.remove(temp)
                    return ("Pending")

    os.remove(temp)
    return("Image")

def main():
    filterPDF()
    workbook.close()
    end = time.time()
    runtime = (end - start)/60
    print(f"Runtime: {runtime} minutes")   
if __name__ == "__main__":
    main()


