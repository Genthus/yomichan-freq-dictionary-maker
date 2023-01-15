import tempfile
import os
import json
import shutil
import re
from zipfile import ZipFile

def extractFreq(s):
    temp = re.findall(r'\[(.*?)\]', s)
    freqString = temp[0]
    if '?' in freqString:
        return '?'
    freqInt = int(re.findall(r'\d+',freqString)[0])
    if 'k' in freqString:
        freqInt *= 1000
    return freqInt

def createFreqFile(fileName, data):
    with open(fileName, 'w', encoding='utf-8') as f:
        json.dump(data, f)

def zipFiles(fileName, files):
    with ZipFile(fileName, 'w') as zip:
        for file in files:
            zip.write(file)

def createFreqDict(path):
    tempFolder = os.path.join(tempfile.gettempdir(),'dictCreation')
    try:
        shutil.rmtree(tempFolder)
    except FileNotFoundError:
        print("")
    os.mkdir(tempFolder)

    with ZipFile(path) as zip:
        zip.extractall(tempFolder)

    files = []

    dictData = {}
    with open(os.path.join(tempFolder,'index.json'),encoding='utf-8') as f:
        dictData = json.load(f)
    dictData['frequencyMode'] = 'occurence-based'
    indexFileName = os.path.join(tempFolder,'index.json')
    createFreqFile(indexFileName,dictData)
    files.append(indexFileName)

    for file in os.listdir(tempFolder):
        newTerms = []
        if "term_bank" in file:
            with open(os.path.join(tempFolder,file),encoding='utf-8') as f:
                terms = json.load(f)
            assert len(terms) > 0, 'no terms found'
            for t in terms:
                freq = extractFreq(t[6])
                newTerms.append([t[0],'freq',freq])
        fileName = 'term_meta_bank_'+ str(len(files)+1)
        fileName = os.path.join(tempFolder,fileName)
        createFreqFile(fileName,newTerms)
        files.append(fileName)

    zipFiles('freq-'+dictData['title'], files)
    shutil.rmtree(tempFolder)

def main():
    for root, _, files in os.walk('.'):
        for file in files:
            if '.zip' in file:
                createFreqDict(os.path.join(root,file))
