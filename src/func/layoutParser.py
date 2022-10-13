from src.dbfunc import sqlfunc, jsonfunc
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

def getSubredditsByTag(tag):
    defaultFont = externalFuncs.getDefaultFont()
    width, height = [int(x/4) for x in sg.Window.get_screen_size()]

    def createColumn(layout,scrollbars=True):
        return sg.Column(layout, scrollable=scrollbars, vertical_scroll_only=True, size=(width,height))
    
    subreddits = jsonfunc.loadData()[tag]

    if len(subreddits) > 40:
            del subreddits[40:]
    
    subColumn = createColumn([[sg.Text("No Gaggles with that tag", font=(defaultFont,12), auto_size_text=True)]], scrollbars=False)

    if not subreddits:
        return subColumn

    userDB = externalFuncs.initUserDB()

    def BT(subreddit): # BT = Button Type
        inSubreddit = subreddit in userDB["userData"].getSubredditData("subreddit")

        return {
            "actionProtocol": "explore_leave_subreddit-" if inSubreddit else "explore_join_subreddit-",
            "actionColor": ("white","red") if inSubreddit else ("white", "green"),
            "subredditColor":("white", sg.theme_background_color()) if externalFuncs.isThemeDark() else ("black", sg.theme_background_color()),
            "actionText": "Leave" if inSubreddit else "Join"
        }

    subColumn = [
        [sg.T("\n"), sg.Button("g/" + subreddit, font=(defaultFont,15), button_color=BT(subreddit)["subredditColor"], border_width=0, key="explore_open_subreddit-" + subreddit), sg.Push(), sg.Button( BT(subreddit)["actionText"], button_color= BT(subreddit)["actionColor"], key=BT(subreddit)["actionProtocol"] + subreddit )] for subreddit in subreddits
    ]

    return createColumn(subColumn)


def getClosestMatchSubreddit(searchFor):
    defaultFont = externalFuncs.getDefaultFont()
    width, height = [int(x/4) for x in sg.Window.get_screen_size()]

    def createColumn(layout,scrollbars=True):
        return sg.Column(layout, scrollable=scrollbars, vertical_scroll_only=True, size=(width,height))

    subColumn = createColumn([[sg.Text("No Gaggles with that name", font=(defaultFont,12), auto_size_text=True)]],scrollbars=False)

    if not searchFor:
        return subColumn

    userDB = externalFuncs.initUserDB()

    sqlfunc.selectDB("postData")
    subResults = sqlfunc.searchData("subreddits","name",searchFor,fetchAll=True)
    tags = jsonfunc.loadData()
    
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

    w,h = sg.Window.get_screen_size()
    w,h = int(w/10.5), 1

    postCards = []
    defaultFont = externalFuncs.getDefaultFont()
    megaphoneButton = externalFuncs.getButton("megaphone")
    buttonColor = ("white" if externalFuncs.isThemeDark() else "black", sg.theme_background_color())
    userDB = externalFuncs.initUserDB()

    for param in params:
        identity = externalFuncs.getPostIdentity(param, mode=str)
        data = externalFuncs.getPostFileData(identity)

        if data["type"] != "text": continue

        w,h = sg.Window.get_screen_size()
        w,h = int(w/20), int(h/len(data["body"])//10)

        exceedsLimit = len(data["body"]) > 100

        postCard = [
            [sg.Text(data["title"], font=(defaultFont,23)), sg.Push(), sg.Button("@" + data["author"], font=(defaultFont,15), button_color= buttonColor, border_width=0, key="postOpenUser_" + data["author"]),
            sg.Button("g/" + data["subreddit"], font=(defaultFont,14), button_color= buttonColor, border_width=0, key="postOpenSubreddit_" + data["subreddit"])],
            [sg.Push(), sg.Button(image_filename=megaphoneButton, image_subsample=9, font=(defaultFont, 15), button_color= buttonColor, border_width=0, key="postHonk_" + identity),
            sg.Text(str(userDB["postData"].getHonks(data["uuid"])), font=(defaultFont,15), text_color= "yellow" if externalFuncs.isThemeDark() else "blue", key="postHonks_" + identity)],
            [sg.Text(data["body"][0:100] + (" ..." if exceedsLimit else ""), font=(defaultFont, 13), size=(w,h))],
            #[sg.Text(data["body"], font=(defaultFont, 13), size= (w,h) )],
            [sg.T("⠀" * 150, size=(w,h))],
            [sg.Button("View", font=(defaultFont, 15), button_color= buttonColor, border_width=1, k="textPostView_" + identity)],
            [sg.HSep()]
        ]
        postCards.extend(postCard)

    return postCards

def imagePostCard(*params):

    w,h = sg.Window.get_screen_size()
    w,h = int(w/10.5), 1

    postCards = []
    defaultFont = externalFuncs.getDefaultFont()
    buttonColor = ("white" if externalFuncs.isThemeDark() else "black", sg.theme_background_color())
    megaphoneButton = externalFuncs.getButton("megaphone")
    userDB = externalFuncs.initUserDB()

    for param in params:
        identity = externalFuncs.getPostIdentity(param, mode=str)
        data = externalFuncs.getPostFileData(identity)
        if data["type"] != "image": continue
        
        postCard = [
            [sg.Text(data["title"], font=(defaultFont,23)), sg.Push(), sg.Button("@" + data["author"], font=(defaultFont,14), button_color= buttonColor, border_width=0, key="postOpenUser_" + data["author"]),
             sg.Button("g/" + data["subreddit"], font=(defaultFont,14), button_color= buttonColor, border_width=0, key="postOpenSubreddit_" + data["subreddit"])],
            [sg.Push(), sg.Button(image_filename=megaphoneButton, image_subsample=9, font=(defaultFont, 15), button_color= buttonColor, border_width=0, key="postHonk_" + identity),
             sg.Text(str(userDB["postData"].getHonks(data["uuid"])), font=(defaultFont,15), text_color= "yellow" if externalFuncs.isThemeDark() else "blue", key="postHonks_" + identity)],
            [sg.Button(image_data=imageFuncs.loadResizedImageB64(data["url"], 200), button_color= buttonColor, border_width=0, key="imagePostOpen_" + identity)],
            [sg.T("⠀" * 150, size=(w,h))],
            [sg.Button("View", font=(defaultFont, 15), button_color=buttonColor, border_width=1, k="imagePostView_" + identity)],
            [sg.HSep()]
        ]
        postCards.extend(postCard)

    return postCards
        
def videoPostCard(*params):

    w,h = sg.Window.get_screen_size()
    w,h = int(w/10.5), 1

    postCards = []
    defaultFont = externalFuncs.getDefaultFont()
    buttonColor = ("white" if externalFuncs.isThemeDark() else "black", sg.theme_background_color())
    megaphoneButton = externalFuncs.getButton("megaphone")
    userDB = externalFuncs.initUserDB()
    for param in params:
        identity = externalFuncs.getPostIdentity(param, mode=str)
        data = externalFuncs.getPostFileData(identity)
        if data["type"] != "video": continue
        
        postCard = [
            [sg.Text(data["title"], font=(defaultFont,23)), sg.Push(), sg.Button("@" + data["author"], font=(defaultFont,14), button_color= buttonColor, border_width=0, key="postOpenUser_" + data["author"]),
            sg.Button("g/" + data["subreddit"], font=(defaultFont,14), button_color= buttonColor, border_width=0, key="postOpenSubreddit_" + data["subreddit"])],
            [sg.Push(), sg.Button(image_filename=megaphoneButton, image_subsample=9, font=(defaultFont, 15), button_color= buttonColor, border_width=0, key="postHonk_" + identity),
             sg.Text(str(userDB["postData"].getHonks(data["uuid"])), font=(defaultFont,15), text_color= "yellow" if externalFuncs.isThemeDark() else "blue", key="postHonks_" + identity)],
            [sg.Button(image_data=imageFuncs.loadResizedImageB64( imageFuncs.getFirstFrameOfVideo(data["url"]), 200), button_color= buttonColor, border_width=0, key="videoPostOpen_" + identity)],
            [sg.T("⠀" * 150, size=(w,h))],
            [sg.Button("View", font=(defaultFont, 15), button_color=buttonColor, border_width=1, k="videoPostView_" + identity)],
            [sg.HSep()]
        ]

        postCards.extend(postCard)

    return postCards

def postCardHandler(*uuids):
    cards = []
    
    for uuid in uuids:
        id = externalFuncs.getPostIdentity(uuid)
        postType = externalFuncs.getPostFileData(id)["type"]

        if postType == "text":
            cards.extend(textPostCard(uuid))
        elif postType == "image":
            cards.extend(imagePostCard(uuid))
        elif postType == "video":
            cards.extend(videoPostCard(uuid))

    return cards

def getComments(uuid=None, username=None, mode="post"):  
    # mode = post | profile

    buttonColor = ("white" if externalFuncs.isThemeDark() else "black", sg.theme_background_color())

    cards = []
    userDB = externalFuncs.initUserDB()
    comments = userDB["postData"].getCommentsBy(post_uuid=uuid, username=username)

    for comment in comments:
        authorpfp = imageFuncs.convertToB64(imageFuncs.convertToPFP(imageFuncs.getPFP(comment["author"]), (50,50)))
        defaultFont = externalFuncs.getDefaultFont()
        isAuthorOfComment = userDB["dataTables"].username.lower() == comment["author"].lower()

        layout = [
            [sg.Image(data=authorpfp), sg.Button("@" + comment["author"], font=(defaultFont,10), button_color= buttonColor, border_width=0, key="postOpenUser_" + comment["author"]), sg.Push(), sg.Text( externalFuncs.prettyDate(comment["dateCreated"]) )],
            [sg.Push(), sg.Button("Delete", k="deleteComment_" + comment["uuid"], button_color="red") if isAuthorOfComment else sg.T()],
            [sg.Text(comment["content"], font=(defaultFont, 12))],
            [sg.HSep()]
        ]

        if mode == "profile":
            # Note that this automatically assumes you're viewing the comment in a profile and prefixes keys with "profile"
            uuid = userDB["postData"].getPostsBy( uuid=comment["post_uuid"], fetchAll=False )[2]
            identity = externalFuncs.getPostIdentity(uuid)
            title = externalFuncs.getPostFileData(identity)["title"]
            postHeader = [
                [sg.Button(title, font=(defaultFont, 15), button_color= buttonColor, border_width=0, key="profileCommentOpenParentPost_" + comment["post_uuid"] + "_fake")]
            ]
            layout = postHeader + layout

        cards.extend(layout)
    return cards

def getRandomTags( tags=None ):
    import random
    buttonColor = ("white" if sg.theme_background_color() == "#19232D" else "black", sg.theme_background_color())
    defaultFont = externalFuncs.getDefaultFont()
    tags = tags or list( jsonfunc.loadData().keys() )
    try:
        tags = random.sample(tags, 6)
    except ValueError:
        return [
            [sg.Text("There aren't enough gaggles with diverse tags!\nThis feature needs at least 6 tags", font=(defaultFont, 20), text_color="red")]
        ]
    
    tagsLayout = [ [sg.Button(tag, font=(defaultFont, 14), button_color=buttonColor, border_width=0, key="explore_openTag-" + tag)] for tag in tags]
    for i in range(1, len(tagsLayout), 2):
        tagsLayout[i] = [sg.Push()] + tagsLayout[i]
    
    return [tagsLayout, tags]

# TODO
# 1) Make postCardHandler return a message if there are no subreddits joined to load posts from. - Ill do this last