import argparse
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdftypes import PDFObjRef
import io
from os.path import isfile, isdir, dirname
from os import listdir, walk
import re
from csv import writer
from pathlib import Path

# create some command line args
parser = argparse.ArgumentParser()
parser.add_argument("--annotations", action="store_true", help="Search through annotations (Eg comments)",
                    default=False, required=False)

parser.add_argument("--notext", action="store_true",
                    help="Turns off searching through text (use if you're only looking at comments",
                    default=False, required=False)
parser.add_argument('--recursive',action="store_true",default=False,required=False,
                    help="Goes through folders and subfolders.")

parser.add_argument("-input", type = str, help="Input: accepts a single file or a directory", required=True)

parser.add_argument("-output", type=str,  help="Output: Needs to be directory.", required=True)

parser.add_argument('-regex', type=str, help="What you're looking for, formatted as a regex string", required=True)

parser.add_argument('--directory', help="check directory", default=False, action="store_true", required=False)
# todo. Regex group
args = parser.parse_args()

GlobalDict = {}

def pdfparser(file):
    holdarray = []
    #parse the file. return false if it fails for some reason
    # open as read only binary
    try:
        fp = open(file, 'rb')

        rsrcmgr = PDFResourceManager()
        # because we're opening stirng as a binary, we need something to convert that binary stream into something usable.
        retstr = io.StringIO()
        laparams = LAParams(all_texts=True)
        device = TextConverter(rsrcmgr, retstr, codec='utf-8', laparams=laparams)
        # Create a PDF interpreter object.
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        # Process each page contained in the document.
    except:
        raise IOError
    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
        if not args.notext:
            text = retstr.getvalue()
            holdarray = fillRegexMatches(text,holdarray)

        if args.annotations:
            for annotation in page.annots:
                if isinstance(annotation, PDFObjRef):
                    # I can either put in effort or just try catch. I choose less effort.
                    try:
                        annotdict = annotation.resolve()
                        annotationtext = annotdict['Contents'].decode('utf-8')
                        holdarray= fillRegexMatches(annotationtext, holdarray)
                    except:
                        continue
    return holdarray

def fillRegexMatches(sentencestr,holdarray):
    regex = re.compile(args.regex)
    result = regex.findall(sentencestr)
    # add all matches
    for match in result and result:
        if match not in holdarray:
            holdarray.append(match)
    return holdarray

# windblows and its bloody backslashes
input = args.input.replace('\\','/')
output = args.output.replace('\\','/')
if args.recursive or args.directory:
    input = dirname(input) + '/'


if isdir(output):
    parser.error('output needs to be a file')

if isfile(input):
    if ".pdf" in input[-4:]:
        try:
            foundlist = pdfparser(input)
            GlobalDict[input] = foundlist
        except:
            GlobalDict[input] = "--ERROR OPENING--"

elif isdir(input) and not args.recursive:
    for file in listdir(input):
         if ".pdf" in file[-4:]:
            print(file)
            file = '{}{}'.format(input,file)
            try:
                foundlist = pdfparser(file)
                GlobalDict[file] = foundlist
            except:
                print("error opening {}".format(file))
                GlobalDict[file] = "--ERROR OPENING--"

elif isdir(input) and args.recursive:
    for directory,subdir, file in walk(input):
        if ".pdf" in file[-4:]:
            print(file)
            file = '{}{}{}'.format(directory,subdir, file)
            try:
                foundlist = pdfparser(file)
                GlobalDict[file] = foundlist
            except:
                print("error opening {}".format(file))
                GlobalDict[file] = "--ERROR OPENING--"

with open(output, 'w',newline='') as csvfile:
    csvdata = writer(csvfile)
    for key, listitems in GlobalDict.items():
        mylist = []
        mylist.append(key)
        for item in listitems:
            mylist.append(item)
        csvdata.writerow(mylist)
csvfile.close()
