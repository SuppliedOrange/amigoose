import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs
from src.func import layoutParser as lp

def postsLayout(username):
    defaultFont = externalFuncs.getDefaultFont()
    comment_button = externalFuncs.getButton("comment")
    profile_button = imageFuncs.convertToPFP( imageFuncs.getPFP(username) ,(200,200), cacheOutput=(username, "user"))
    sg.theme(externalFuncs.getTheme())
    buttonColor = externalFuncs.getThemeBackground()
    userDB = externalFuncs.initUserDB()

    postsLayout = [
        [sg.Button(image_filename=profile_button, image_subsample=1, button_color=buttonColor, border_width=0, key="profile+posts_open_profile-" + username), sg.Push(),
        sg.Button(image_filename=comment_button, image_subsample=9, button_color=buttonColor, border_width=0, key="profile+posts_open_comments-" + username)],
        [sg.HSep()],
        [sg.Column(
            [*lp.postCardHandler(
                *[x[2] for x in userDB["postData"].getPostsBy(author=username)]
            )],
            scrollable=True, vertical_scroll_only=True, expand_x=True, expand_y=True, sbar_relief=sg.RELIEF_FLAT
        )]
    ]
    
    return postsLayout

def postsExec(event,values,window):
    if (event == "profile+posts_open_profile"):
        externalFuncs.moveTab(window, "profileTabgroup", "postsTab", "profileTab")
    elif (event == "profile+posts_open_comments"):
        externalFuncs.moveTab(window, "profileTabgroup", "postsTab", "commentsTab")

posts = externalFuncs.TabElement(exec=postsExec, layout=postsLayout)