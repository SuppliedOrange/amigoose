import json
from src.func.externalFuncs import getPath
fp = getPath("./subreddits/tags/tags.json")

def loadData():
    data = open(fp)
    data = json.load(data)
    return data

def updateData(updateKey:str,updateValue:list):
    data = loadData()
    with open(fp, "w") as jsonFile:
        data[updateKey] = updateValue
        json.dump(data, jsonFile)

def updateFile(dct:dict):
    with open(fp, "w") as jsonFile:
        json.dump(dct, jsonFile)