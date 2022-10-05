import json
from src.func.externalFuncs import getPath
fp = getPath("./subreddits/tags/tags.json")


def loadData():
    """
    Load all values from the /subreddits/tags/tags.json file.\n
    Returns a dictionary.
    """
    data = open(fp)
    data = json.load(data)
    return data


def updateData(updateKey: str, updateValue: list):
    """
    Modify a tag's subreddits in /subreddits/tags/tags.json\n
    \n
    updateKey - String - Tag to update\n
    updateValue - List - New list of subreddits for this tag
    """
    data = loadData()
    with open(fp, "w") as jsonFile:
        data[updateKey] = updateValue
        json.dump(data, jsonFile)


def updateFile(dct: dict):
    """
    Update /subreddits/tags/tags.json as a whole\n
    \n
    dct - Dictionary - The JSON dictionary/array to dump into the JSON file.
    """
    with open(fp, "w") as jsonFile:
        json.dump(dct, jsonFile)
