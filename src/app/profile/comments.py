import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs, layoutParser

def commentsLayout(username):
    defaultFont = externalFuncs.getDefaultFont()
    posts_button = externalFuncs.getButton("post")
    profile_button = imageFuncs.convertToPFP( imageFuncs.getPFP(username) ,(200,200), cacheOutput=(username, "user"))
    sg.theme(externalFuncs.getTheme())
    buttonColor = externalFuncs.getThemeBackground()

    headerLayout = [
        [sg.Button(image_filename=profile_button, image_subsample=1, button_color=buttonColor, border_width=0, key="profile+comments_open_profile-" + username), sg.Push(),
        sg.Button(image_filename=posts_button, image_subsample=9, button_color=buttonColor, border_width=0, key="profile+comments_open_posts-" + username)],
    ]
    
    commentsLayout = [
        [sg.Column(
            [ *layoutParser.getComments(username=username, mode="profile") ], scrollable=True, sbar_relief=sg.RELIEF_FLAT, sbar_background_color=externalFuncs.getThemeBackground(), expand_x=True, expand_y=True
        )]
    ]

    commentsLayout = headerLayout + commentsLayout

    return commentsLayout

def commentsExec(event,values,window):
    if (event == "profile+comments_open_profile"):
        externalFuncs.moveTab(window, "profileTabgroup", "commentsTab", "profileTab")
    elif (event == "profile+comments_open_posts"):
        externalFuncs.moveTab(window, "profileTabgroup", "commentsTab", "postsTab")

comments = externalFuncs.TabElement(exec=commentsExec, layout=commentsLayout)