import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs, layoutParser

def viewPostTextWindow(postIdentity, parent=None):

    back_button = externalFuncs.getButton("back_button")
    buttonColor = externalFuncs.getThemeBackground()
    defaultFont = externalFuncs.getDefaultFont()
    megaphoneButton = externalFuncs.getButton("megaphone")
    commentButton = externalFuncs.getButton("comment")
    userDB = externalFuncs.initUserDB()
    post = externalFuncs.postIdentityExtractor(postIdentity)
    post = externalFuncs.getPostFileData(post["subreddit"], post["author"], post["uuid"])
    width, height = [int(x/2) for x in sg.Window.get_screen_size()]

    w,h = sg.Window.get_screen_size()
    w,h = int(w/10), int(h/len(post["body"])//10)

    authorpfp = imageFuncs.convertToPFP(imageFuncs.getPFP(post["author"]) or externalFuncs.getPath("./assets/amigoose_assets/defaultGoose.png"), (75,75))

    sg.theme(externalFuncs.getTheme())

    viewPostTextLayout = [
        [sg.Button(image_filename=back_button, image_subsample=12, button_color= buttonColor, border_width=0, key="viewPostTextClose_" + postIdentity)],
        [sg.Text(post["title"], font=(defaultFont,30)), sg.Push(),
         sg.Button(image_filename=authorpfp,button_color=buttonColor, border_width=0, key="viewPostTextOpenAuthor_" + post["author"])],
        [sg.Text(post["body"], font=(defaultFont, 13), size=(w,h))],
        [sg.T()],
        [sg.Button(image_filename=commentButton, image_subsample=9, font=(defaultFont, 15), button_color= buttonColor, border_width=0, key="commentPost_" + postIdentity),
         sg.Button(image_filename=megaphoneButton, image_subsample=9, font=(defaultFont, 15), button_color= buttonColor, border_width=0, key="postHonk_" + postIdentity),
         sg.Text(str(userDB["postData"].getHonks(post["uuid"])), font=(defaultFont,15), text_color= "yellow" if externalFuncs.isThemeDark() else "blue", key="postHonks_" + postIdentity)],
        [sg.Text()],
        [sg.HSep()],
        layoutParser.getComments(post["uuid"])
    ]

    viewPostTextLayout = [
        [sg.Column(
            viewPostTextLayout, scrollable=True, sbar_relief=sg.RELIEF_FLAT, sbar_background_color=externalFuncs.getThemeBackground(), expand_x=True, expand_y=True
        )]
    ]

    window = sg.Window( (post["title"][0:30] + (" ..." if len(post["title"]) > 30 else "")) , viewPostTextLayout.copy(), size=(width,height), resizable=True, alpha_channel=userDB["settings"].getPreference("opacity"),icon=imageFuncs.getLogo(), metadata={
        "parent": parent,
        "postIdentity": postIdentity
    })

    window.finalize()
    return window

def viewPostTextWatch(window):
    
    event,values = window.read(100)
    event = externalFuncs.sanitizeEvent(event, allowNumbers=True)

    method, value = (None, None) if not event or len(event.split("_")) != 2 else event.split("_")

    if(event==sg.WIN_CLOSED):
        window.close()
        return (True,True) # break, no failure

    elif (event == "viewPostTextClose_" + window.metadata["postIdentity"]):
        window.close()
        from src.func.parentHandler import parentHandler
        if window.metadata["parent"]: parentHandler(window.metadata["parent"])
        return (True,True) # break, no failure
    
    elif (method == "viewPostTextOpenAuthor"):
        window.close()
        parent = {"type": "viewPostText", "layoutArgs": (window.metadata["postIdentity"], window.metadata["parent"])}
        profileArgs = (value, None, parent)
        from src.app.profile.profile import profile
        profile.start(argsWindow=profileArgs)
        return (True, True)

    externalFuncs.postFunctionHandler(event, values, window)

viewPostText = externalFuncs.WinElement(viewPostTextWatch, window=viewPostTextWindow)