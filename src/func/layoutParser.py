from xml.dom.minidom import Identified
from src.dbfunc import sqlfunc
from src.func import externalFuncs, imageFuncs
import PySimpleGUI as sg
import pickle

def getClosestMatchUsers(searchFor):
    
    defaultFont = externalFuncs.getDefaultFont()
    confirm_button = externalFuncs.getButton("confirm")
    buttonColor = externalFuncs.getThemeBackground()
    sqlfunc.selectDB("settings")
    userResults = sqlfunc.searchData("preferences","username",searchFor,fetchAll=True)
    userColumn = None
    scrollable = True
    if not searchFor or not userResults:
        userColumn = [[sg.Text("No users with that username", font=(defaultFont,12))]]
        scrollable = False # Disable the scrollbar if there are no results.
    else:
        if len(userResults) > 40:
            del userResults[40:]
        userColumn = [
            [sg.T("\n"), sg.Text(user,font=(defaultFont,15)), sg.Push() ,sg.Button(image_filename=confirm_button, image_subsample=20, button_color= buttonColor, border_width=0, key="search_open_profile-" + user)] for user in userResults
        ]
    width, height = [int(x/4) for x in sg.Window.get_screen_size()]
    return sg.Column(userColumn, scrollable=scrollable, vertical_scroll_only=True, size=(width,height))

def getSubredditsForUser(username):
    userDB = externalFuncs.initUserDB(username)
    defaultFont = externalFuncs.getDefaultFont()
    isThemeDark = externalFuncs.isThemeDark()
    subResults = userDB["userData"].getSubredditData("subreddit")
    subColumn = None
    scrollable = True

    if not subResults:
        subColumn = [[sg.Text("You're not in any gaggles!",font=(defaultFont,12),text_color= "yellow" if isThemeDark else "blue")]]
        scrollable = False
    else:
        if len(subResults) > 40:
            del subResults[40:]

        def interactionButton(subreddit):
            # If the user is the owner of the subreddit, allow them to delete the subreddit. Otherwise, give them the option to leave it.
            isOwner = (userDB["dataTables"].username == userDB["postData"].getSubreddits(subreddit, "owner")[0])
            return sg.Button("Delete", button_color="red", key="delete_subreddit-" + subreddit) if isOwner else sg.Button("Leave", button_color="red", key="leave_subreddit-" + subreddit)
        
        subColumn = [
            [sg.T("\n"), sg.Text("g/" + subreddit, font=(defaultFont,15)), sg.Push(), interactionButton(subreddit)] for subreddit in subResults
        ]

    width, height = [int(x/4) for x in sg.Window.get_screen_size()]
    layout = [sg.Column(subColumn, scrollable=scrollable, vertical_scroll_only=True, size=(width,height), sbar_relief=sg.RELIEF_FLAT)]
    return layout

def getClosestMatchSubreddit(searchFor):
    defaultFont = externalFuncs.getDefaultFont()
    width, height = [int(x/4) for x in sg.Window.get_screen_size()]

    def createColumn(layout,scrollbars=True):
        return sg.Column(layout, scrollable=scrollbars, vertical_scroll_only=True, size=(width,height))

    subColumn = createColumn([[sg.Text("No Gaggles with that name", font=(defaultFont,12), auto_size_text=True)]],scrollbars=False)

    if not searchFor:
        return subColumn

    userDB = externalFuncs.initUserDB()
    from src.dbfunc.jsonfunc import loadData

    sqlfunc.selectDB("postData")
    subResults = sqlfunc.searchData("subreddits","name",searchFor,fetchAll=True)
    tags = loadData()
    
    if searchFor in tags:
        if len(subResults) > 20:
            del subResults[20:]

        subResults = list(subResults)
        [subResults.append(tag) for tag in tags[searchFor] if tag not in subResults]

        if len(subResults) > 40:
            del subResults[40:]

    if not subResults:
        return subColumn

    else:
        def BT(subreddit): # BT = Button Type
            inSubreddit = subreddit in userDB["userData"].getSubredditData("subreddit")

            return {
                "actionProtocol": "search_leave_subreddit-" if inSubreddit else "search_join_subreddit-",
                "actionColor": ("white","red") if inSubreddit else ("white", "green"),
                "subredditColor":("white", sg.theme_background_color()) if externalFuncs.isThemeDark() else ("black", sg.theme_background_color()),
                "actionText": "Leave" if inSubreddit else "Join"
            }

        subColumn = [
            [sg.T("\n"), sg.Button("g/" + subreddit, font=(defaultFont,15), button_color=BT(subreddit)["subredditColor"], border_width=0, key="search_open_subreddit-" + subreddit), sg.Push(), sg.Button( BT(subreddit)["actionText"], button_color= BT(subreddit)["actionColor"], key=BT(subreddit)["actionProtocol"] + subreddit )] for subreddit in subResults
        ]
        
    return createColumn(subColumn)

def textPostCard(*params):
    postCards = []
    defaultFont = externalFuncs.getDefaultFont()
    megaphoneButton = externalFuncs.getButton("megaphone")
    buttonColor = ("white" if externalFuncs.isThemeDark() else "black", sg.theme_background_color())
    userDB = externalFuncs.initUserDB()
    for param in params:
        author = param[0]
        subreddit = param[1]
        uuid = param[2]
        dataFile = externalFuncs.getPath(f'./subreddits/posts/{subreddit}/{author}+{uuid}.dat')
        identity = author + "-" + uuid + "-" + subreddit
        f = open(dataFile,"rb")
        data = pickle.load(f)
        postCard = [
            [sg.Text(data["title"], font=(defaultFont,23)), sg.Push(), sg.Text('By:', font=(defaultFont,15)), sg.Button("@" + data["author"], font=(defaultFont,15), button_color= buttonColor, border_width=0, key="postOpenUser_" + data["author"])],
            [sg.Push(), sg.Button(image_filename=megaphoneButton, image_subsample=9, font=(defaultFont, 15), button_color= buttonColor, border_width=0, key="textPostHonk_" + identity), sg.Text(str(userDB["postData"].getHonks(uuid)), font=(defaultFont,15), text_color= "yellow" if externalFuncs.isThemeDark() else "blue", key="imagePostHonks_" + identity)],
            [sg.Text(data["body"][0:100] + " ->")],
            [sg.HSep()]
        ]
        postCards.extend(postCard)
    return postCards

def imagePostCard(*params):
    postCards = []
    defaultFont = externalFuncs.getDefaultFont()
    buttonColor = ("white" if externalFuncs.isThemeDark() else "black", sg.theme_background_color())
    megaphoneButton = externalFuncs.getButton("megaphone")
    userDB = externalFuncs.initUserDB()
    for param in params:
        author = param[0]
        subreddit = param[1]
        uuid = param[2]
        identity = author + "-" + uuid + "-" + subreddit
        dataFile = externalFuncs.getPath(f'./subreddits/posts/{subreddit}/{author}+{uuid}.dat')
        f = open(dataFile,"rb")
        data = pickle.load(f)
        postCard = [
            [sg.Text(data["title"], font=(defaultFont,23)), sg.Push(), sg.Button("@" + data["author"], font=(defaultFont,14), button_color= buttonColor, border_width=0, key="postOpenUser_" + data["author"]),
             sg.Button("g/" + data["subreddit"], font=(defaultFont,14), button_color= buttonColor, border_width=0, key="postOpenSubreddit_" + data["subreddit"])],
            [sg.Push(), sg.Button(image_filename=megaphoneButton, image_subsample=9, font=(defaultFont, 15), button_color= buttonColor, border_width=0, key="imagePostHonk_" + identity),
             sg.Text(str(userDB["postData"].getHonks(uuid)), font=(defaultFont,15), text_color= "yellow" if externalFuncs.isThemeDark() else "blue", key="imagePostHonks_" + identity)],
            [sg.Button(image_data=imageFuncs.loadResizedImageB64(data["url"], 200), button_color= buttonColor, border_width=0, key="imagePostOpen_" + identity)],
            [sg.HSep()]
        ]
        postCards.extend(postCard)
    return postCards
        
def videoPostCard(*params):
    postCards = []
    defaultFont = externalFuncs.getDefaultFont()
    buttonColor = ("white" if externalFuncs.isThemeDark() else "black", sg.theme_background_color())
    megaphoneButton = externalFuncs.getButton("megaphone")
    userDB = externalFuncs.initUserDB()
    for param in params:
        author = param[0]
        subreddit = param[1]
        uuid = param[2]
        identity = author + "-" + uuid + "-" + subreddit
        dataFile = externalFuncs.getPath(f'./subreddits/posts/{subreddit}/{author}+{uuid}.dat')
        f = open(dataFile,"rb")
        data = pickle.load(f)
        postCard = [
            [sg.Text(data["title"], font=(defaultFont,23)), sg.Push(), sg.Button("@" + data["author"], font=(defaultFont,14), button_color= buttonColor, border_width=0, key="postOpenUser_" + data["author"]),
            sg.Button("g/" + data["subreddit"], font=(defaultFont,14), button_color= buttonColor, border_width=0, key="postOpenSubreddit_" + data["subreddit"])],
            [sg.Push(), sg.Button(image_filename=megaphoneButton, image_subsample=9, font=(defaultFont, 15), button_color= buttonColor, border_width=0, key="videoPostHonk_" + identity),
             sg.Text(str(userDB["postData"].getHonks(uuid)), font=(defaultFont,15), text_color= "yellow" if externalFuncs.isThemeDark() else "blue", key="videoPostHonks_" + identity)],
            [sg.Button(image_data=imageFuncs.loadResizedImageB64( imageFuncs.getFirstFrameOfVideo(data["url"]), 200), button_color= buttonColor, border_width=0, key="videoPostOpen_" + identity)],
            [sg.HSep()]
        ]
        postCards.extend(postCard)
    return postCards

def postCardHandler(*uuids):
    cards = []
    for uuid in uuids:
        userDB = externalFuncs.initUserDB()
        data = userDB["postData"].getPost(uuid)
        author = data[0]
        subreddit = data[1]
        uuid = data[2]
        dataFile = externalFuncs.getPath(f'./subreddits/posts/{subreddit}/{author}+{uuid}.dat')
        f = open(dataFile,"rb")
        typeOfPost = pickle.load(f)["type"]

        if typeOfPost == "text":
            cards.extend(textPostCard(data))
        elif typeOfPost == "image":
            cards.extend(imagePostCard(data))
        elif typeOfPost == "video":
            cards.extend(videoPostCard(data))
    return cards
