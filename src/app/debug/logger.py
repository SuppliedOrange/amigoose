from datetime import datetime
from time import time
from src.func.externalFuncs import getPath

PATH_TO_LOGS = getPath("./logs/logs.txt")
PATH_TO_ERROR_LOGS = getPath("./logs/errorlogs.txt")

def log(record):
    try:
        logFile = open(PATH_TO_LOGS, "w")
        logFile.write(record)
        logFile.close()
    except Exception as e:
        print(e)
        logFile.close()
        pass

def now():
    return datetime.fromtimestamp( time() ).strftime("[%d/%m %Hh:%Mm:%Ss] ")
