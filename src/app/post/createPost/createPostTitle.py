import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs, parentHandler

def createPostTitleWindow(subreddit,existing_title=None,parent=None):
    width, height = [int(x/2) for x in sg.Window.get_screen_size()]
    existing_title = existing_title or "An interesting title"
    defaultFont = externalFuncs.getDefaultFont()
    back_button = externalFuncs.getButton("back_button")
    userDB = externalFuncs.initUserDB()
    buttonColor = externalFuncs.getThemeBackground()

    textPostButton = externalFuncs.getButton("text")
    imagePostButton = externalFuncs.getButton("image")
    videoPostButton = externalFuncs.getButton("video")

    sg.theme(externalFuncs.getTheme())

    profileLayout = [
        [sg.Button(image_filename=back_button, image_subsample=12, button_color= buttonColor, border_width=0, key="createPost_return_home"), sg.Push(),
         sg.Text("g/" + subreddit, text_color="yellow" if externalFuncs.isThemeDark() else "red", font=(defaultFont,20))],
        [sg.T()],
        [sg.Text("Post Title",font=(defaultFont,15))],
        [sg.Push(), sg.InputText(existing_title, background_color=buttonColor[0], size=( int(width/10), 30), font=(defaultFont,20), key="createPost_title" ), sg.Push()],
        # Size of Input Text Box = (width, height) = (screen width / 10, 30 pixels)
        [sg.Push(), sg.Text(key="createPost_charlength")],
        [sg.T()],
        [sg.Text("Post Type",font=(defaultFont,15))],
        [sg.Push(),
         sg.Button(image_filename=textPostButton, image_subsample=4, button_color= buttonColor, border_width=0, key="createPost_createTextPost"), sg.Push(),
         sg.Button(image_filename=imagePostButton, image_subsample=4, button_color= buttonColor, border_width=0, key="createPost_createImagePost"), sg.Push(),
         sg.Button(image_filename=videoPostButton, image_subsample=4, button_color= buttonColor, border_width=0, key="createPost_createVideoPost"), 
         sg.Push()],
    ]
    window = sg.Window("Creating a post..." , profileLayout.copy(), size=(width,height), alpha_channel=userDB["settings"].getPreference("opacity"), icon=imageFuncs.getLogo(), metadata={
        "parent": parent,
        "subreddit": subreddit
    })
    window.finalize()
    return window

isValidTitle = False

def createPostTitleWatch(window):
    global isValidTitle
    event,values = window.read(100)
    event = externalFuncs.sanitizeEvent(event)

    if(event==sg.WIN_CLOSED):
        window.close()
        return (True,True) # break, no failure

    elif (event == "createPost_return_home"):
        window.close()
        if window.metadata["parent"]: parentHandler.parentHandler(window.metadata["parent"])
        return (True, True)
    
    elif (event == "createPost_createTextPost"):
        if checkTitleLength(values["createPost_title"]):
            window.close()
            # existing_title, parent -> createPostTitle args
            parent = {"type":"createPostTitle", "layoutArgs": (window.metadata["subreddit"],values["createPost_title"], window.metadata["parent"])}
            createPostTextArgs = (values["createPost_title"],parent)
            from src.app.post.createPost.createPostText import createPostText
            createPostText.start(argsWindow=createPostTextArgs)
            return (True,True)

    elif (event == "createPost_createImagePost"):
        if checkTitleLength(values["createPost_title"]):
            window.close()
            # existing_title, parent -> createPostTitle args
            parent = {"type":"createPostTitle", "layoutArgs": (window.metadata["subreddit"],values["createPost_title"], window.metadata["parent"])}
            createPostImageArgs = (values["createPost_title"],parent)
            from src.app.post.createPost.createPostImage import createPostImage
            createPostImage.start(argsWindow=createPostImageArgs)
            return (True,True)
    
    elif (event == "createPost_createVideoPost"):
        if checkTitleLength(values["createPost_title"]):
            window.close()
            # existing_title, parent -> createPostTitle args
            parent = {"type":"createPostTitle", "layoutArgs": (window.metadata["subreddit"],values["createPost_title"], window.metadata["parent"])}
            createPostVideoArgs = (values["createPost_title"],parent)
            from src.app.post.createPost.createPostVideo import createPostVideo
            createPostVideo.start(argsWindow=createPostVideoArgs)
            return (True,True)

    if window and values:
        charlength = f"{len(values['createPost_title'])}/60"
        charlengthcolor = "blue" if checkTitleLength(values["createPost_title"]) else "red"
        window["createPost_charlength"].update(charlength,text_color=charlengthcolor)

def checkTitleLength(title):
    return not ((len(title) > 60) or (len(title) < 1))

createPostTitle = externalFuncs.WinElement(createPostTitleWatch, window=createPostTitleWindow) 