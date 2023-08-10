INSTALLATION REQUIREMENTS:
using pip install:
    pandas
    xlsxwriter
    pymupdf
    fitz
    glob
    pytesseract
    pdf2image
    python-poppler (More details on this in the Test/imageToText/requirements.txt file)


INITIALIZATION:
    1. Place the data excel or csv file in the data DIRECTORY
    2. Ensure that in the data file, the first row are the headers for the column

    In the main code, wordSeach.py: 
    3. On line 14, change the path to the location where the data is installed.
    4. On line 61, chose between pd.read_csv(data_url) and pd.read_excel(data_url) depending on the format of the data file.
    5. On line 64 and 70, add any other words that you need to search for.
    6. On line 92 and 94, change the string in data["string"] to the column name of the well number and links to the reports
    according to the data file.


SUMMARY OF THE DIRECTORY:
    - The Archives directory contains the past versions of the code and a failed tentative to make the code run faster
    - The data directory contains the data file from which the wells need to be sorted
    - the Test directory contains tests to run each parts of the main code as well as other attemps to implement new methods/processes.
    - The source.txt contains the sources from which some parts of the code are taken from before modifying them to fit the program.
    - There is a version of the program with comments describing each steps and one with comments.

SUMMARY OF THE MAIN CODE:
    The program works by taking a excel file or a pdf and loading it in python as a pandas dataset.
    From the dataset, the two useful columns of well number and report links are taken.
    For each entries/row in the dataset, the link is requested from the web and opened as a pdf file.
    The file is then searched through page by page by matching each words in the wordlists.
    If the pdf is an image, there are 2 choices:
        - Either it is considered as an image and directly writen in the excel file
        - Or it is first converted to an image file then serached
    If a word from the wordlist is present in the page, the program will classify it in the predetermined classes 
    and will write them in the corresponding column in the excel file.
    
    The program print the progression rate (number of file/total file) everytime a file is processed.
    When the program ends, it will print out the runtime, the total time it took to run the code.

POST-RUN:
  - Change the name of the excel file so that the content will not be replaced if the code is activated again.

