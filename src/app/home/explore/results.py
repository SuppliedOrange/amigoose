import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs, layoutParser as lp

def resultsWindow(tag, parent=None):
    width, height = [int(x/2) for x in sg.Window.get_screen_size()]

    defaultFont = externalFuncs.getDefaultFont()
    isThemeDark = externalFuncs.isThemeDark()
    back_button = externalFuncs.getButton("back_button")
    sg.theme(externalFuncs.getTheme())
    buttonColor = externalFuncs.getThemeBackground()

    resultsLayout = [
        [sg.Button(image_filename=back_button, image_subsample=9, button_color= externalFuncs.getThemeBackground(), border_width=0, key="results_return_home" )],
        [sg.Text(f"Gaggles tagged with \"{tag}\"", font=(defaultFont,30))],
        [lp.getSubredditsByTag(tag)]
    ]

    window = sg.Window("Amigoose - explore" , resultsLayout.copy(),size=(width,height), resizable=True, alpha_channel=externalFuncs.getWindowOpacity(), icon=imageFuncs.getLogo(), metadata={
        "parent": parent
    })
    window.finalize()
    return window

def resultsWatch(window):
    event,values = window.read(100)

    try: method, value = event.split("-")
    except: method, value = None, None

    if(event==sg.WIN_CLOSED or event == "results_return_home"):
        window.close()
        from src.func.parentHandler import parentHandler
        if window.metadata["parent"]: parentHandler(window.metadata["parent"])
        return (True,True) # break, no failure       

    elif (method == "explore_open_subreddit"):
        from src.app.subreddit.subreddit import subreddit
        # subreddit, opentab, parent
        argsForSubreddit = (value, None, window.metadata["parent"])
        window.close()
        subreddit.start(argsWindow=argsForSubreddit)
        return (True, True)

results = externalFuncs.WinElement(resultsWatch, window=resultsWindow)