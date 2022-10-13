import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs, parentHandler
import pickle
from time import time
import uuid

chosenVideoPath = None

def createPostVideoWindow(title,parent):
    width, height = [int(x/2) for x in sg.Window.get_screen_size()]
    defaultFont = externalFuncs.getDefaultFont()
    back_button = externalFuncs.getButton("back_button")
    confirm_button = externalFuncs.getButton("confirm")
    defaultOpenVideoButton = imageFuncs.loadResizedImageB64(externalFuncs.getButton("open_file"), 200)
    userDB = externalFuncs.initUserDB()
    buttonColor = externalFuncs.getThemeBackground()
    subreddit = parent["layoutArgs"][0] # Get subreddit name from parent object.

    sg.theme(externalFuncs.getTheme())

    profileLayout = [
        [sg.Button(image_filename=back_button, image_subsample=12, button_color= buttonColor, border_width=0, key="createPostVideo_return_home"), sg.Push(),
        sg.Text("g/" + subreddit, text_color="yellow" if externalFuncs.isThemeDark() else "red", font=(defaultFont,20))],
        [sg.Text(title,font=(defaultFont,15))],
        [sg.VPush()],
        [sg.Push(), sg.Button(image_data=defaultOpenVideoButton, button_color=buttonColor, border_width=0, k="createPostVideo_open_video"), sg.Push()],
        [sg.VPush()],
        [sg.Text("No image selected",text_color="red",key="createPostVideo_filepath_name"), sg.Push(), sg.Button(image_filename=confirm_button, image_subsample=15, button_color=buttonColor,border_width=0,key="createPostVideo_confirm")]
    ]
    window = sg.Window("Creating a post..." , profileLayout.copy(), size=(width,height), resizable=True, alpha_channel=userDB["settings"].getPreference("opacity"), icon=imageFuncs.getLogo(), metadata={
        "parent": parent,
        "title": title
    })
    window.finalize()
    return window

def createPostVideoWatch(window):
    event,values = window.read(100)
    event = externalFuncs.sanitizeEvent(event)
    global chosenVideoPath

    if(event==sg.WIN_CLOSED):
        window.close()
        return (True,True) # break, no failure

    elif (event == "createPostVideo_return_home"):
        window.close()
        if window.metadata["parent"]: parentHandler.parentHandler(window.metadata["parent"])
        return (True, True)
    
    elif (event == "createPostVideo_open_video"):
        video_file_path = sg.popup_get_file("Select a video file to post",no_window=True,icon=imageFuncs.getLogo("light"),file_types=(("Video Files",".mov .mp4 .wmv .avi .flv"),))
        if (imageFuncs.checkVideo(video_file_path)):
            window["createPostVideo_open_video"].update(image_data=imageFuncs.loadResizedImageB64(imageFuncs.getFirstFrameOfVideo(video_file_path), 200))
            window["createPostVideo_filepath_name"].update(externalFuncs.getBasename(video_file_path),text_color="blue")
            chosenVideoPath = video_file_path
        else:
            sg.popup_quick_message("Not a video file! Honk!")

    elif (event == "createPostVideo_confirm"):
        if (chosenVideoPath):

            userDB = externalFuncs.initUserDB()
            POST_ID = uuid.uuid4().hex
            AUTHOR = externalFuncs.sqlfunc.existingUser().lower()
            SUBREDDIT = window.metadata["parent"]["layoutArgs"][0]
            TIMENOW = int(time())
            postName = f'{AUTHOR}+{POST_ID}.dat'
            videoName = f'{AUTHOR}+{POST_ID}' + imageFuncs.Path(chosenVideoPath).suffix
            postPath = externalFuncs.getPath("./subreddits/posts/" + SUBREDDIT + "/" + postName)
            VIDEO_PATH = imageFuncs.copyFile(chosenVideoPath, externalFuncs.getPath("./assets/user_assets/post_videos/"), videoName)

            post_object = {
                "type": "video",
                "uuid": POST_ID,
                "author": AUTHOR,
                "time": TIMENOW,
                "subreddit": SUBREDDIT,
                "title": window.metadata["title"],
                "url": VIDEO_PATH
            }

            with open(postPath, 'wb') as f:
                pickle.dump(post_object, f)

            userDB["postData"].createPostMap(AUTHOR, SUBREDDIT, POST_ID, VIDEO_PATH, TIMENOW)

            window.close()
            postIdentity = AUTHOR + "-" + POST_ID + "-" + SUBREDDIT
            from src.app.post.viewPost.viewPostVideo import viewPostVideo
            viewPostVideo.start(postIdentity)
            return (True, True)

createPostVideo = externalFuncs.WinElement(createPostVideoWatch, window=createPostVideoWindow)