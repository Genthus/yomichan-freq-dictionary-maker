import tempfile
import os
import json
import shutil
import re
from zipfile import ZipFile

# Change this function to suit the way the dictionary logs its frequency
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
        json.dump(data, f, ensure_ascii=False)

def zipFiles(fileName, files):
    with ZipFile(fileName, 'w') as zip:
        for file in files:
            zip.write(file, arcname = os.path.basename(file))
            print('added ' + os.path.basename(file))

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
                freq = extractFreq(t[5][0]) # change this to the field where the frequency is
                newTerms.append([t[0],'freq',freq])
            fileName = 'term_meta_bank_'+ str(len(files)) + '.json'
            fileName = os.path.join(tempFolder,fileName)
            createFreqFile(fileName,newTerms)
            files.append(fileName)

    zipName = 'freq-'+dictData['title']+'.zip'
    try:
        os.remove(zipName)
    except FileNotFoundError:
        print("")
    zipFiles(zipName, files)
    shutil.rmtree(tempFolder)
    print('finished!')

def main():
    for root, _, files in os.walk('.'):
        for file in files:
            if '.zip' in file and 'freq' not in file:
                createFreqDict(os.path.join(root,file))

if __name__ == "__main__":
    main()
