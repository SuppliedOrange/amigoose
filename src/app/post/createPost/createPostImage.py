import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs, parentHandler
import pickle
import uuid
from time import time

chosenImagePath = None

def createPostImageWindow(title,parent):
    width, height = [int(x/2) for x in sg.Window.get_screen_size()]
    defaultFont = externalFuncs.getDefaultFont()
    back_button = externalFuncs.getButton("back_button")
    confirm_button = externalFuncs.getButton("confirm")
    defaultOpenImageButton = imageFuncs.loadResizedImageB64(externalFuncs.getButton("open_file"), 200)
    userDB = externalFuncs.initUserDB()
    buttonColor = externalFuncs.getThemeBackground()
    subreddit = parent["layoutArgs"][0] # Get subreddit name from parent object.

    sg.theme(externalFuncs.getTheme())

    profileLayout = [
        [sg.Button(image_filename=back_button, image_subsample=12, button_color= buttonColor, border_width=0, key="createPostImage_return_home"), sg.Push(),
        sg.Text("g/" + subreddit, text_color="yellow" if externalFuncs.isThemeDark() else "red", font=(defaultFont,20))],
        [sg.Text(title,font=(defaultFont,15))],
        [sg.VPush()],
        [sg.Push(), sg.Button(image_data=defaultOpenImageButton, button_color=buttonColor, border_width=0, k="createPostImage_open_image"), sg.Push()],
        [sg.VPush()],
        [sg.Text("No image selected",text_color="red",key="createPostImage_filepath_name"), sg.Push(), sg.Button(image_filename=confirm_button, image_subsample=15, button_color=buttonColor,border_width=0,key="createPostImage_confirm")]
    ]
    window = sg.Window("Creating a post..." , profileLayout.copy(), size=(width,height), resizable=True, alpha_channel=userDB["settings"].getPreference("opacity"), icon=imageFuncs.getLogo(), metadata={
        "parent": parent,
        "title": title
    })
    window.finalize()
    return window

def createPostImageWatch(window):
    event,values = window.read(100)
    event = externalFuncs.sanitizeEvent(event)
    global chosenImagePath

    if(event==sg.WIN_CLOSED):
        window.close()
        return (True,True) # break, no failure

    elif (event == "createPostImage_return_home"):
        window.close()
        if window.metadata["parent"]: parentHandler.parentHandler(window.metadata["parent"])
        return (True, True)
    
    elif (event == "createPostImage_open_image"):
        image_file_path = sg.popup_get_file("Select an image file to post",no_window=True,icon=imageFuncs.getLogo("light"),file_types=(("Image Files",".png .jpg .jpeg .gif .svg .webp .bmp"),))
        if (imageFuncs.checkImage(image_file_path)):
            window["createPostImage_open_image"].update(image_data=imageFuncs.loadResizedImageB64(image_file_path, 200))
            window["createPostImage_filepath_name"].update(externalFuncs.getBasename(image_file_path),text_color="blue")
            chosenImagePath = image_file_path
        else:
            sg.popup_quick_message("Not an image file! Honk!")

    elif (event == "createPostImage_confirm"):
        if (chosenImagePath):

            userDB = externalFuncs.initUserDB()
            POST_ID = uuid.uuid4().hex
            AUTHOR = externalFuncs.sqlfunc.existingUser().lower()
            SUBREDDIT = window.metadata["parent"]["layoutArgs"][0]
            TIMENOW = int(time())
            postName = f'{AUTHOR}+{POST_ID}.dat'
            postPath = externalFuncs.getPath("./subreddits/posts/" + SUBREDDIT + "/" + postName)
            imageName = f'{AUTHOR}+{POST_ID}.png'
            #imageFuncs.Path(chosenImagePath).suffix
            IMAGE_PATH = imageFuncs.convertImage(chosenImagePath,externalFuncs.getPath("./assets/user_assets/post_images/" + imageName))
            #IMAGE_PATH = imageFuncs.copyFile(chosenImagePath, externalFuncs.getPath("./assets/user_assets/post_images/"), imageName)
            post_object = {
                "type": "image",
                "uuid": POST_ID,
                "author": AUTHOR,
                "time": TIMENOW,
                "subreddit": SUBREDDIT,
                "title": window.metadata["title"],
                "url": IMAGE_PATH
            }

            with open(postPath, 'wb') as f:
                pickle.dump(post_object, f)

            userDB["postData"].createPostMap(AUTHOR, SUBREDDIT, POST_ID, IMAGE_PATH, TIMENOW)

            window.close()
            sg.popup_ok("Aight done. now link em to the post.")
            return (True, True)

createPostImage = externalFuncs.WinElement(createPostImageWatch, window=createPostImageWindow)