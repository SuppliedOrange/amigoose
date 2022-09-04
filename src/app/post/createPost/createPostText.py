import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs, parentHandler
import pickle
import uuid
from time import time

def createPostTextWindow(title,parent):
    width, height = [int(x/2) for x in sg.Window.get_screen_size()]
    defaultFont = externalFuncs.getDefaultFont()
    back_button = externalFuncs.getButton("back_button")
    confirm_button = externalFuncs.getButton("confirm")
    userDB = externalFuncs.initUserDB()
    buttonColor = externalFuncs.getThemeBackground()
    subreddit = parent["layoutArgs"][0] # Get subreddit name from parent object.

    sg.theme(externalFuncs.getTheme())

    profileLayout = [
        [sg.Button(image_filename=back_button, image_subsample=12, button_color= buttonColor, border_width=0, key="createPostText_return_home"), sg.Push(),
        sg.Text("g/" + subreddit, text_color="yellow" if externalFuncs.isThemeDark() else "red", font=(defaultFont,20))],
        [sg.Text(title,font=(defaultFont,15))],
        [sg.HSep()],
        [sg.Multiline(font=(defaultFont,10), size=(130,15), background_color="gray" if externalFuncs.isThemeDark() else "white", border_width=0, key="createPostText_content")],
        [sg.HSep()],
        [sg.Text(key="createPostText_charlength"), sg.Push(), sg.Button(image_filename=confirm_button, image_subsample=15, button_color=buttonColor,border_width=0,key="createPostText_confirm")]
    ]
    window = sg.Window("Creating a post..." , profileLayout.copy(), size=(width,height), alpha_channel=userDB["settings"].getPreference("opacity"), icon=imageFuncs.getLogo(), metadata={
        "parent": parent,
        "title": title
    })
    window.finalize()
    return window

def createPostTextWatch(window):
    event,values = window.read(100)
    event = externalFuncs.sanitizeEvent(event)

    if(event==sg.WIN_CLOSED):
        window.close()
        return (True,True) # break, no failure

    elif (event == "createPostText_return_home"):
        window.close()
        if window.metadata["parent"]: parentHandler.parentHandler(window.metadata["parent"])
        return (True, True)
    
    elif (event == "createPostText_confirm"):
        if (checkContentLength(values)):

            userDB = externalFuncs.initUserDB()
            POST_ID = uuid.uuid4().hex
            AUTHOR = userDB["dataTables"].username.lower()
            SUBREDDIT = window.metadata["parent"]["layoutArgs"][0]
            TIMENOW = int(time())
            postName = f'{AUTHOR}+{POST_ID}.dat'
            postPath = externalFuncs.getPath("./subreddits/posts/" + SUBREDDIT + "/" + postName)
            post_object = {
                "type": "text",
                "uuid": POST_ID,
                "author": AUTHOR,
                "time": TIMENOW,
                "subreddit": SUBREDDIT,
                "title": window.metadata["title"],
                "body": values["createPostText_content"]
            }

            # Making the pickle
            with open(postPath, 'wb') as f:
                pickle.dump(post_object, f)
            
            userDB["postData"].createPostMap(AUTHOR, SUBREDDIT, POST_ID, None, TIMENOW)

            window.close()
            sg.popup_ok("Aight done. now link em to the post.")
            return (True, True)

    if window and values:
        charlength = f"{len(values['createPostText_content'])}/1000"
        charlengthcolor = "blue" if checkContentLength(values) else "red"
        window["createPostText_charlength"].update(charlength,text_color=charlengthcolor)


def checkContentLength(values):
    return not ((len(values['createPostText_content']) > 1000) or (len(values['createPostText_content']) < 1))

createPostText = externalFuncs.WinElement(createPostTextWatch, window=createPostTextWindow)