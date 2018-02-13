from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
from pymongo import MongoClient

import glob
import datetime

parsed_pdf_path = './Parsed PDF/*.txt'
files = glob.glob(parsed_pdf_path)

def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text

if __name__ == '__main__':
    source_files = glob.glob('./Data/Argometer/12/*.pdf')

    for file in source_files:
        new_file_name = '12-' + file.split('\\')[1].split()[0] + '.txt'
        print(new_file_name)

        with open(new_file_name, 'w') as output_file:
            output_file.write(convert_pdf_to_txt(file))