import PySimpleGUI as sg
from src.func import externalFuncs
from src.func import layoutParser as lp


def homeLayout():
    settings_icon = externalFuncs.getButton("settings_icon")
    defaultFont = externalFuncs.getDefaultFont()
    amigoose_logo = externalFuncs.getButton("amigoose_logo")
    sg.theme(externalFuncs.getTheme())
    userDB = externalFuncs.initUserDB()
    width, height = sg.Window.get_screen_size()
    height, width = int(height/1.2), int(width/1.2)
    buttonColor = ("white" if sg.theme_background_color() ==
                   "#19232D" else "black", sg.theme_background_color())
    user = userDB["dataTables"].username
    subredditsForUser = userDB["userData"].getSubredditData("subreddit", user)

    homeLayout = [
        [sg.Image(amigoose_logo, subsample=10), sg.Push(), sg.Button(image_filename=settings_icon, image_subsample=8,
                                                                     button_color=externalFuncs.getThemeBackground(), border_width=0, key="home_open_settings")],
        [sg.Button("me", font=(defaultFont, 23), button_color=buttonColor, border_width=0, key="home_open_user_profile"),
         sg.Button("find", font=(defaultFont, 23),
                   button_color=buttonColor, border_width=0, key="home_search"),
         sg.Button("open", font=(defaultFont, 23), button_color=buttonColor, border_width=0, key="home_open_opensub")],
        [sg.HSep()],
        [sg.Column(
            [*lp.postCardHandler(
                *[x[2] for x in userDB["postData"].getPostsBySubredditList(subreddits=subredditsForUser)]
            )],
            scrollable=True, vertical_scroll_only=True, expand_x=True, expand_y=True, sbar_relief=sg.RELIEF_FLAT
        )]
    ]

    return homeLayout


def homeExec(event, values, window):

    # Dealing with window/tab open events
    if (event == "home_open_settings"):
        externalFuncs.moveTab(window, "tabgroup", "homeTab", "settingsTab")
    elif (event == "home_open_user_profile"):
        from src.app.profile.profile import profile
        profile.start()
    elif (event == "home_search"):
        from src.app.home.search.search import search
        search.start()
    elif (event == "home_open_opensub"):
        from src.app.opensub.opensub import opensub
        opensub.start()

    # Dealing with post stuff
    externalFuncs.postFunctionHandler(event, values, window)


hlg = externalFuncs.TabElement(exec=homeExec, layout=homeLayout)
