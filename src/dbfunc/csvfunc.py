import csv
from time import time

DELIMITER = "|"
FILE_PATH = FP = r"users\blocked\blocked.csv"
HEADER = ["Blocker", "Blockee", "Initiated On"]

def checkFileExists(fp=FP):
    try: return bool(open(FP))
    except FileNotFoundError: return False

def initFile(): # Fixes pretty much everything in the file. Run this on startup.
    if not checkFileExists():
        with open(FP, "w", newline="\n") as f:
            writer = csv.writer(f, delimiter=DELIMITER)
            writer.writerow(HEADER)
    else:
        with open(FP, newline="\n") as f:
            reader = list(csv.reader(f, delimiter=DELIMITER))
            if not reader or reader[0] != HEADER:
                with open(FP, "w", newline="\n") as f2:
                    reader.insert(0, HEADER)
                    writer = csv.writer(f2, delimiter=DELIMITER)
                    writer.writerows(reader)
                    f2.flush()

def searchFor(blocker, blockee):
    with open(FP, newline="\n") as f:
        reader = list(csv.reader(f, delimiter=DELIMITER))[1::] # [1::] To skip the first element of the list, the header
        try: return list(filter(lambda x: x[0] == blocker and x[1] == blockee, reader))[0]
        except IndexError: return []

def getIndexOfBlock(blocker, blockee): # (Including header)
    with open(FP, newline="\n") as f:
        reader = list(csv.reader(f, delimiter=DELIMITER))[1::]
        try: return reader.index( searchFor(blocker, blockee) ) + 1
        except ValueError: return []

def getBlockedUsersFor(blocker):
    with open(FP, newline="\n") as f:
        reader = list(csv.reader(f, delimiter=DELIMITER))[1::]
        return [x[1] for x in reader if x[0] == blocker]

def addBlock(blocker, blockee):
    TIMENOW = int(time())
    if searchFor(blocker,blockee): return False # If the block is already in effect
    with open(FP, "a+", newline="\n") as f:
        writer = csv.writer(f, delimiter=DELIMITER)
        writer.writerow([blocker, blockee, TIMENOW])
        f.flush()
        return True # Success

def removeBlock(blocker, blockee):
    blockToRemove = searchFor(blocker, blockee)
    with open(FP, newline="\n") as f:
        reader = list(csv.reader(f, delimiter=DELIMITER))[1::]
    with open(FP, "w", newline="\n") as f:
        writer = csv.writer(f, delimiter=DELIMITER)
        try:
            reader.remove( blockToRemove )
            writer.writerows([HEADER, *reader])
            f.flush()
            return True # Success
        except ValueError:
            writer.writerows([HEADER, *reader])
            return False # If the block log doesn't exist