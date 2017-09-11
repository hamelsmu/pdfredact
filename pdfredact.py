#!/usr/bin/env python

from PyPDF2 import PdfFileReader
import PyPDF2 as pyPdf
import PyPDF2 as pdf
from os.path import isfile, join
from os import listdir
import argparse

def _setup_page_id_to_num(pdf, pages=None, _result=None, _num_pages=None):
    if _result is None:
        _result = {}
    if pages is None:
        _num_pages = []
        pages = pdf.trailer["/Root"].getObject()["/Pages"].getObject()
    t = pages["/Type"]
    if t == "/Pages":
        for page in pages["/Kids"]:
            _result[page.idnum] = len(_num_pages)
            _setup_page_id_to_num(pdf, page.getObject(), _result, _num_pages)
    elif t == "/Page":
        _num_pages.append(1)
    return _result

def outlines_pg_zoom_info(outlines, pg_id_num_map, result=None):
    if result is None:
        result = dict()
    if type(outlines) == list:
        for outline in outlines:
            result = outlines_pg_zoom_info(outline, pg_id_num_map, result)
    elif type(outlines) == pyPdf.pdf.Destination:
        title = outlines['/Title']
        result[title] = pg_id_num_map[outlines.page.idnum]+1

    return result

def getOutlines(path):
    f = open(path,'rb')
    pdf = PdfFileReader(f)
    pg_id_num_map = _setup_page_id_to_num(pdf)
    outlines = pdf.getOutlines()
    bookmarks_info = outlines_pg_zoom_info(outlines, pg_id_num_map)
    return bookmarks_info


def redact(mypath, fname):
    fullpath = join(mypath, fname)
    redactedpath = join(mypath, 'redacted_'+fname)
    #Open Document For Reading
    doc = pdf.PdfFileReader(fullpath)
    output = pdf.pdf.PdfFileWriter()
    output.setPageMode('/UseOutlines')

    #Crop Pages
    for page in doc.pages:
        # Change last parameter to change height at which page gets cropped.
        # The larger the numbers the less it gets cropped was at 715 before
        page.cropBox = pdf.generic.RectangleObject([0, 0, 612, 564])
        output.addPage(page)

    #Parse Original Bookmark, and Transfer Them To New PDF
    for v,k in sorted([(v, k) for (k,v) in getOutlines(fullpath).items() if ',' not in k]):
        output.addBookmark(k, v-1)

    #Write File
    with open(redactedpath, "wb") as outputStream:
        output.write(outputStream)

if __name__ == '__main__':
    import os
    mypath = os.getcwd()
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) if '.pdf' in f and 'redacted' not in f]

    if len(onlyfiles) == 0:
        raise Exception("No pdf files to process in directory")

    else:
        for f in onlyfiles:
            print('Redacting', join(mypath, f))
            redact(mypath, f)
