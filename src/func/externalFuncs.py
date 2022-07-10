# All the functions that are used throughout the entire app.

import os
from src.dbfunc import sqlfunc,dataTables

def moveTab(window,tabgroup,fromTab,toTab):
    """
    Moves from one tab to another, deselecting the older tab.
    """
    window[tabgroup].Widget.select(window.metadata['tabs'].index(toTab))
    deselectTab(window,fromTab)

def deselectTab(window,tab):
    """
    Hides a tab.
    """
    window[tab].update(visible=False)

def getFonts():
    """
    Get all current installed fonts on the user's computer.
    """
    from tkinter import font
    import tkinter
    root = tkinter.Tk()
    fonts = list(font.families())
    root.destroy()
    return fonts

def initUserDB(username=sqlfunc.existingUser()):
    """
    Create a new data table for the specified user (or current user)
    """
    userDB = dataTables.dataTables(username).initializeUser()
    return userDB

def getPath(path):
    """
    Returns an absolute path from a relative path.
    """
    return os.path.abspath(path)

def isThemeDark(user=sqlfunc.existingUser()):
    """
    Returns a boolean indicating whether the current theme is dark or not.
    """
    userDB = initUserDB(user)
    try:
        isThemeDark = (userDB["settings"].getPreference("theme") == "DarkGrey8")
    except:
        isThemeDark = False # Probably because this is being called before logging in
    return isThemeDark

def getDefaultFont(user=sqlfunc.existingUser()):
    """
    Get the current preferred font for the specified user (otherwise current user) from database.
    """
    userDB = initUserDB(user)
    return userDB["settings"].getPreference("font")

def getButton(button_name,invert=False):
    """
    Returns a path to amigoose_assets/(button_name)_[color]\n\n

    invert - Boolean - Whether to invert the colour of the image
    """

    if not invert:
        button = getPath(f"./assets/amigoose_assets/{button_name}_{'light' if isThemeDark() else 'dark'}.png")
    else:
        button = getPath(f"./assets/amigoose_assets/{button_name}_{'dark' if isThemeDark() else 'light'}.png")
    return button

def playHonk():
    import vlc
    p = vlc.MediaPlayer(getPath("./assets/amigoose_assets/HJONK.mp3"))
    p.play()

def getTheme(user=sqlfunc.existingUser()):
    """
    Get the current preferred theme for the specified user (otherwise current user) from database.
    """
    userDB = initUserDB(user)
    return userDB["settings"].getPreference("theme")

def getThemeBackground():
    """
    Returns the button-color or for transparent buttons to use.
    > (theme_bg_colour,theme_bg_colour)
    """
    import PySimpleGUI as sg
    return (sg.theme_background_color(),sg.theme_background_color())

def checkIfExists(username):
    """
    Responds with a boolean indicating whether the provided name is the name of a user.
    """
    sqlfunc.selectDB("accounts")
    usernames = sqlfunc.loadColumn("passwords","username")
    return username in usernames

def isSubreddit(subreddit):
    """
    Responds with a boolean indicating whether the provided name is a name of a subreddit.
    """
    sqlfunc.selectDB("postData")
    subreddits = sqlfunc.loadColumn("subreddits","name")
    return subreddit in subreddits

def checkIllegalInput(value):
    """
    Checks if text is a potential SQL Injection
    Value - Text to check - String
    """
    return all(map(lambda x: x not in value,[";","'","\"", " OR "]))

def subredditNameValidator(name):
    """
    Validates a name for a Gaggle
    name - Name to check - String
    """

    if not checkIllegalInput(name):
        return (False, "Chosen Gaggle name is forbidden.")

    if len(name) < 1 or len(name) > 20:
        return (False, "Gaggle name length must be 1-20 characters")
    if " " in name:
        return (False, "Gaggle name cannot contain spaces")
    
    sqlfunc.selectDB("postData")
    checkExist = sqlfunc.getData("subreddits",("name", name), "name", fetchAll=True)
    if checkExist:
        return (False, "Gaggle \"" + name + "\" already exists.")

    validChars = list("1234567890qwertyuiopasdfghjklzzxcvbnm/.|_@")
    if not all(letter.lower() in validChars for letter in name):
        return (False, "Your gaggle name can only alphanumeric and . @ _ | characters.")
    
    return (True,)

def getWindowOpacity():
    """ Gets the user's preference of window opacity """
    userDB = initUserDB()
    return userDB["settings"].getPreference("opacity")

def sanitizeEvent(event):
    """
    Sometimes while nesting windows, the events have numbers allocated to them so that they don't get mixed.\n
    This removes those numbers by selecting only the alphabets, - and _ characters.\n
    Event - Event to check - String
    """
    import re
    return re.search("([a-zA-Z_\+-]+)", event).group(1) if event and re.search("([a-zA-Z_\+-]+)", event) else None

def getBasename(filePath):
    """
    Returns the basename of the file path\n\n
    filePath - String - Path to the file
    """
    return os.path.basename(filePath)

class WinElement():
    """
    Window Element. PySimpleGUI window controller I made for easy access.\n\n

    Parameters -> run (PySimpleGUI watcher), window (PySimpleGUI window)

    **.start()** -> Starts the window and it's watcher.\n
    Arguments: \n
    argsWindow [ Make a window with specific arguments ]\n\n

    **.stop()** -> Stops the window.\n
    Arguments: \n
    noKill | restart [ Stops the window but not it's watcher. Restarts the window. ]\n
    argsWin [ Arguments for the next time the window restarts, if it does. ]\n

    """
    def __init__(self,run,window):
        self.run = run
        self.makeWindow = window

    def start(self, argsWindow=None, argsWatch=None):

        def parseArgs(args):
            # This will make all args into a tuple
            return (args,) if not args is None and type(args) != tuple else args

        argsWindow = parseArgs(argsWindow)
        argsWatch = parseArgs(argsWatch)

        self.window = self.makeWindow(*argsWindow) if argsWindow else self.makeWindow()
        self.restart = False
        result = False
        while True:
            if (self.restart):
                self.restart = False
                break
            toBreak = self.run(self.window,*argsWatch) if argsWatch else self.run(self.window)
            if (toBreak and toBreak[0]):
                if (toBreak[1]):
                    result = toBreak[1]
                    break
                else:
                    exit(0)
        return result

    def stop(self,restart=False,noKill=False, argsWin=None, argsWatch=None):
        if noKill or restart:
            self.restart = True    

        if restart:
            self.window.close()
            return self.start(argsWindow=argsWin,argsWatch=argsWatch)
        
        return self.window.close()
        

class TabElement():
    """
    Tab Element. PySimpleGUI Tab controller I made for easy access\n\n
    
    Exec is the tab watcher which continuously scans for tab events, similar to window watcher.\n
    Layout is the pre-generated tab layout that the user can switch to.\n\n

    **.getLayout()** -> Returns the tab's layout.\n
    argsLayout [ arguments for generating the tab layout ]\n
    """
    def __init__(self,layout,exec):
        self.exec = exec
        self.layout = layout
    def getLayout(self,argsLayout=None):
        return (self.layout(argsLayout) if argsLayout else self.layout()).copy()