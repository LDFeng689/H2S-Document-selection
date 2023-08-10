#Import packages
import pandas as pd
import xlsxwriter as excel
import fitz
import re
import requests

#Just too see more of the data during tests
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

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
              #all other variants
            ] 

def filterPDF():
    number = data["Number"]
    pdfLinks = data["Link to inspection report"]
    rowH2S = 2
    rowImg = 2
    rowNot =2

    for i in range(len(pdfLinks)):

        if type(pdfLinks[i]) is not float:      #conditional to filter out the wells that have no links ("None" in the xlsx is consider as a float, while links are strings)
            if wordSearch(pdfLinks[i], wordList) == "Present":
                worksheet.write(rowH2S,0, number[i], cell_format)
                worksheet.write(rowH2S,1, pdfLinks[i], cell_format)
                rowH2S+=1
            elif wordSearch(pdfLinks[i], wordList) == "Image":
                worksheet.write(rowImg,4, number[i], cell_format)
                worksheet.write(rowImg,5, pdfLinks[i], cell_format)
                rowImg+=1
            else:
                worksheet.write(rowNot,8, number[i], cell_format)
                worksheet.write(rowNot,9, pdfLinks[i], cell_format)
                rowNot+=1
        i +=1

def wordSearch(url, target: [str]):
    # open the pdf file
    res = requests.get(url)
    reader = fitz.open(stream = res.content, filetype = "pdf")

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
        


def main():
    filterPDF()
    workbook.close()

if __name__ == "__main__":
    main()


