# import packages
import PyPDF2
import re
import io
from urllib.request import Request, urlopen


url = "https://sigpeg.mrn.gouv.qc.ca/rapport/A161_insp_inactif_2019-06-12_Publique.pdf"
remote_file = urlopen(Request(url)).read()
memory_file = io.BytesIO(remote_file)
reader = PyPDF2.PdfReader(memory_file)


# define key terms
string = ["Indices"]
# get number of pages
num_pages = len(reader.pages)
image_count = 0
# extract text and do the search
for page in reader.pages:
    text = page.extract_text() 
    if text == "":
        image_count +=1
        continue
    res_search = re.search(string[0], text)
    if res_search is not None:
        print(1)
        break

if image_count == num_pages:   #not sure if really useful, cause if 1 image, prob the rest are all images
    print("Image")
    #print(res_search)

# open the pdf file
#reader = PyPDF2.PdfReader(url)