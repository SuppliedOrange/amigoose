import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs, layoutParser

def viewPostVideoWindow(postIdentity, parent=None):

    back_button = externalFuncs.getButton("back_button")
    buttonColor = externalFuncs.getThemeBackground()
    defaultFont = externalFuncs.getDefaultFont()
    megaphoneButton = externalFuncs.getButton("megaphone")
    commentButton = externalFuncs.getButton("comment")
    userDB = externalFuncs.initUserDB()
    post = externalFuncs.getPostFileData(postIdentity)
    width, height = [int(x/2) for x in sg.Window.get_screen_size()]

    authorpfp = imageFuncs.convertToB64(imageFuncs.convertToPFP(imageFuncs.getPFP(post["author"]) or externalFuncs.getPath("./assets/amigoose_assets/defaultGoose.png"), (50,50)))

    sg.theme(externalFuncs.getTheme())

    headerLayout = [
        [sg.Button(image_filename=back_button, image_subsample=12, button_color= buttonColor, border_width=0, key="viewPostVideoClose_" + postIdentity)],
        [sg.Text(post["title"], font=(defaultFont,30)), sg.Push(),
         sg.Button(image_data=authorpfp,button_color=buttonColor, border_width=0, key="viewPostVideoOpenAuthor_" + post["author"])],
    ]

    actionButtonLayout = [
        sg.Button(image_filename=commentButton, image_subsample=9, font=(defaultFont, 15), button_color= buttonColor, border_width=0, key="commentPost_" + postIdentity),
        sg.Button(image_filename=megaphoneButton, image_subsample=9, font=(defaultFont, 15), button_color= buttonColor, border_width=0, key="postHonk_" + postIdentity),
        sg.Text(str(userDB["postData"].getHonks(post["uuid"])), font=(defaultFont,15), text_color= "yellow" if externalFuncs.isThemeDark() else "blue", key="postHonks_" + postIdentity)
        ]

    if (userDB["dataTables"].username == post["author"]):
        from random import choice
        delete_quotes = ["Deletus.", "Commit Unpost.", "Unalive post.", "Dileet Post"]
        actionButtonLayout.extend([
            sg.Push(), sg.Button(choice(delete_quotes), button_color="red", key="viewPostDelete_" + postIdentity)
        ])

    viewPostVideoLayout = [
        [sg.Button(image_data=imageFuncs.loadResizedImageB64( imageFuncs.getFirstFrameOfVideo(post["url"]) , 400), button_color= buttonColor, border_width=0, key="videoPostOpen_" + postIdentity)],
        [sg.T()],
        actionButtonLayout,
        [sg.T()],
        [sg.HSep()],
        *layoutParser.getComments(post["uuid"])
    ]

    viewPostVideoLayout = [
        [sg.Column(
            viewPostVideoLayout, scrollable=True, sbar_relief=sg.RELIEF_FLAT, sbar_background_color=externalFuncs.getThemeBackground(), expand_x=True, expand_y=True
        )]
    ]

    viewPostVideoLayout = headerLayout + viewPostVideoLayout

    window = sg.Window( (post["title"][0:30] + (" ..." if len(post["title"]) > 30 else "")) , viewPostVideoLayout.copy(), size=(width,height), resizable=True, alpha_channel=userDB["settings"].getPreference("opacity"),icon=imageFuncs.getLogo(), metadata={
        "parent": parent,
        "postIdentity": postIdentity
    })

    window.finalize()
    return window

def viewPostVideoWatch(window):
    
    event,values = window.read(100)
    event = externalFuncs.sanitizeEvent(event, allowNumbers=True)


    method, value = (None, None) if not event or len(event.split("_")) != 2 else event.split("_")

    if(event==sg.WIN_CLOSED):
        window.close()
        return (True,True) # break, no failure
    
    elif (event == "viewPostVideoClose_" + window.metadata["postIdentity"]):
        window.close()
        from src.func.parentHandler import parentHandler
        if window.metadata["parent"]: parentHandler(window.metadata["parent"])
        return (True,True) # break, no failure
    
    elif (method == "viewPostVideoOpenAuthor"):
        window.close()
        parent = {"type": "viewPostVideo", "layoutArgs": (window.metadata["postIdentity"], window.metadata["parent"])}
        profileArgs = (value, None, parent)
        from src.app.profile.profile import profile
        profile.start(argsWindow=profileArgs)
        return (True, True)

    externalFuncs.postFunctionHandler(event, values, window)

viewPostVideo = externalFuncs.WinElement(viewPostVideoWatch, window=viewPostVideoWindow)