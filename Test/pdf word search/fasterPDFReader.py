import fitz
import re
import io
from urllib.request import Request, urlopen
import requests

url = "https://sigpeg.mrn.gouv.qc.ca/rapport/A161_insp_inactif_2019-06-12_Publique.pdf"
#remote_file = urlopen(Request(url)).read()
#memory_file = io.BytesIO(remote_file)
#print(memory_file)
res = requests.get(url)
reader = fitz.open(stream = res.content, filetype = "pdf")



# define key terms
string = ["Non"]
# get number of pages
num_pages = reader.page_count
image_count = 0
# extract text and do the search
for i in range(num_pages):
    text = reader.load_page(i)
    text = text.get_text() 
    if text == "":
        print(2)
        break
    res_search = re.search(string[0], text)
    if res_search is not None:
        print(1)
        break