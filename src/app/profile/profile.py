import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs
from src.dbfunc import sqlfunc
from datetime import datetime

from .posts import posts
from .comments import comments

def profileWindow(username=sqlfunc.existingUser(), openTab=None ,parent=None):
    width, height = [int(x/1.5) for x in sg.Window.get_screen_size()]

    openTab = openTab or "profileTab"
    defaultFont = externalFuncs.getDefaultFont()
    back_button = externalFuncs.getButton("back_button")
    comment_button = externalFuncs.getButton("comment")
    posts_button = externalFuncs.getButton("post")
    userDB = externalFuncs.initUserDB(username)
    pfp = imageFuncs.convertToPFP(imageFuncs.getPFP(username) or externalFuncs.getPath("./assets/amigoose_assets/defaultGoose.png"), (200,200))
    date_join = datetime.utcfromtimestamp( userDB["userData"].getProfileData("accountCreated")[0] ).strftime("%d/%m/%Y")
    bio = userDB["userData"].getProfileData("bio")[0]
    buttonColor = externalFuncs.getThemeBackground()

    sg.theme(externalFuncs.getTheme())

    profileLayout = [
        [sg.Button(image_filename=back_button, image_subsample=12, button_color= buttonColor, border_width=0, key="profile_return_home-" + username ), sg.Push(),
         sg.Button(image_filename=posts_button, image_subsample=9, button_color=buttonColor, border_width=0, key="profile_open_posts-" + username),
         sg.Button(image_filename=comment_button, image_subsample=9, button_color=buttonColor, border_width=0, key="profile_open_comments-" + username)],
        [sg.Image(pfp), sg.Push(), sg.Text(username, font=(defaultFont,40))],
        [sg.T('')],
        [sg.Text("Joined: " + date_join, font=(defaultFont,12)), sg.Push(), sg.Text("Honks: " + str(userDB["userData"].getProfileData("honks")[0]), font=(defaultFont,12))],
        [sg.Text(f"\"{bio}\"" if bio else "", font=(defaultFont,12), size=(50,30))]
    ]

    tabs = [
        sg.Tab("Profile - " + username,profileLayout,key='profileTab'),
        sg.Tab("Posts - " + username, posts.getLayout(username), key="postsTab"),
        sg.Tab("Comments - " + username, comments.getLayout(username), key="commentsTab")
    ]

    profileLayout = [[sg.TabGroup([tabs], key='profileTabgroup', expand_x=True, expand_y=True)]]
    window = sg.Window("@" + username ,profileLayout.copy(),size=(width,height), resizable=True, alpha_channel=userDB["settings"].getPreference("opacity"),icon=imageFuncs.convertToB64(pfp), metadata={
        "tabs": list(map(lambda x: x.Key ,tabs)),
        "username": username,
        "parent": parent
    })

    window.finalize()
    for tab in window.metadata["tabs"]:
        if tab != openTab: externalFuncs.deselectTab(window,tab)
    return window

def profileWatch(window):
    
    event,values = window.read(100)
    event = externalFuncs.sanitizeEvent(event)

    method,value = event.split("-") if event and "-" in event else (None,None)

    if value == window.metadata["username"]:
        event = event.split("-")[0]

    if(event==sg.WIN_CLOSED):
        window.close()
        return (True,True) # break, no failure

    if (event == "profile_return_home"):
        window.close()
        from src.func.parentHandler import parentHandler
        if window.metadata["parent"]: parentHandler(window.metadata["parent"])
        return (True,True) # break, no failure
    
    elif (event == "profile_open_posts"):
        externalFuncs.moveTab(window,"profileTabgroup","profileTab","postsTab")

    elif (event == "profile_open_comments"):
        externalFuncs.moveTab(window,"profileTabgroup","profileTab","commentsTab")

    v = (event,values,window)

    posts.exec(*v)
    comments.exec(*v)

profile = externalFuncs.WinElement(profileWatch, window=profileWindow)