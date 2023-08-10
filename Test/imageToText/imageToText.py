import pytesseract
from pdf2image import convert_from_path
import glob
import re
import requests
import os

target = ["foss", "valeur"]
temp = "Test/imageToText/temp.pdf"

url = "https://sigpeg.mrn.gouv.qc.ca/rapport/A119_insp_inactif_2019-05-08_Publique.pdf"
res = requests.get(url)

with open(temp, "wb") as file:
    PDFbyte = file.write(res.content)

pdfs = glob.glob(temp)

for pdf_path in pdfs:
    pages = convert_from_path(pdf_path, 500)   #converts pdf to pillow image

    for pageNum,imgBlob in enumerate(pages):
        text = pytesseract.image_to_string(imgBlob,lang='eng')     #convert the image to strings
        #do the search since text should be a string
        #with open(f'{pdf_path[:-4]}_page{pageNum}.txt', 'w') as the_file:
         #   the_file.write(text) 

        for j in range(len(target)):
            res_search = re.search(target[j], text)   #for each elements in the list "target", we do a word search by pattern matching in each page of the pdf
            if res_search is not None:
                print(1)
            else:
                print(2)
os.remove(temp)






#pdfs = glob.glob(res)

#print(pdfs)
#print(reader)

"""

for pdf_path in pdfs:
    pages = convert_from_path(pdf_path, 500)   #converts pdf to pillow image

    for pageNum,imgBlob in enumerate(pages):
        text = pytesseract.image_to_string(imgBlob,lang='eng')     #convert the image to strings
        #do the search since text should be a string
        #with open(f'{pdf_path[:-4]}_page{pageNum}.txt', 'w') as the_file:
         #   the_file.write(text) 

        for j in range(len(target)):
            res_search = re.search(target[j], text)   #for each elements in the list "target", we do a word search by pattern matching in each page of the pdf
            if res_search is not None:
                print(1)
            else:
                print(2)


#function for the main one
def imageSearch(path):
    pdfs = glob.glob(path)
    for pdf_path in pdfs:
        pages = convert_from_path(pdf_path, 500) 
        for pageNum,imgBlob in enumerate(pages):
            text = pytesseract.image_to_string(imgBlob,lang='eng')
            for j in range(len(target)):
                res_search = re.search(target[j], text)   #for each elements in the list "target", we do a word search by pattern matching in each page of the pdf
                if res_search is not None:
                    return("Present")
                else:
                    j+=1
    return("Image")

"""