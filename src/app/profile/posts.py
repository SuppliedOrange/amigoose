import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs

def postsLayout(username):
    defaultFont = externalFuncs.getDefaultFont()
    comment_button = externalFuncs.getButton("comment")
    profile_button = imageFuncs.convertToPFP( imageFuncs.getPFP(username) ,(200,200), cacheOutput=(username, "user"))
    sg.theme(externalFuncs.getTheme())
    buttonColor = externalFuncs.getThemeBackground()

    postsLayout = [
        [sg.Button(image_filename=profile_button, image_subsample=3, button_color=buttonColor, border_width=0, key="profile+posts_open_profile-" + username), sg.Push(),
        sg.Button(image_filename=comment_button, image_subsample=9, button_color=buttonColor, border_width=0, key="profile+posts_open_comments-" + username)],
        [sg.Text("load the posts here.",font=(defaultFont,15))]
    ]
    
    return postsLayout

def postsExec(event,values,window):
    if (event == "profile+posts_open_profile"):
        externalFuncs.moveTab(window, "profileTabgroup", "postsTab", "profileTab")
    elif (event == "profile+posts_open_comments"):
        externalFuncs.moveTab(window, "profileTabgroup", "postsTab", "commentsTab")

posts = externalFuncs.TabElement(exec=postsExec, layout=postsLayout)