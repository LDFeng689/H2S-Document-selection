# import packages
import PyPDF2
import re

url = "test\pdf word search\P_A004_inspection_2018-11-01_publique.pdf"

# open the pdf file
reader = PyPDF2.PdfReader(url)


# define key terms
string = ["travaux", "patate"]

# extract text and do the search
for page in reader.pages:
    text = page.extract_text() 
    # print(text)
    res_search = re.search(string[0], text)
    if res_search is not None:
        print(1)
        break
    #print(res_search)

#works for local pdf files
