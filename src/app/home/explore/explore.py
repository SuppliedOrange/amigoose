import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs, layoutParser as lp

def exploreWindow(tags=None):
    width, height = [int(x/2) for x in sg.Window.get_screen_size()]

    defaultFont = externalFuncs.getDefaultFont()
    isThemeDark = externalFuncs.isThemeDark()
    back_button = externalFuncs.getButton("back_button")
    sg.theme(externalFuncs.getTheme())
    buttonColor = externalFuncs.getThemeBackground()
    try: tagsList, tags = lp.getRandomTags(tags)
    except: tagsList, tags = lp.getRandomTags(tags), "No Tags"

    exploreLayout = [
        [sg.Button(image_filename=back_button, image_subsample=9, button_color= externalFuncs.getThemeBackground(), border_width=0, key="explore_return_home" )],
        [sg.Text("Pick a tag", font=(defaultFont,30))],
        *tagsList
    ]

    window = sg.Window("Amigoose - explore" , exploreLayout.copy(),size=(width,height), resizable=True, alpha_channel=externalFuncs.getWindowOpacity(),icon=imageFuncs.getLogo(),metadata={
        "tags": tags
    })
    window.finalize()
    return window

def exploreWatch(window):
    event,values = window.read(100)

    try: method, value = event.split("-")
    except: method, value = None, None

    if(event==sg.WIN_CLOSED or event == "explore_return_home"):
        window.close()
        return (True,True) # break, no failure
    
    elif (method == "explore_openTag"):
        from .results import results
        parent = { "type": "explore", "layoutArgs": window.metadata["tags"] }
        window.close()
        results.start(argsWindow=(value, parent))
        return (True, True)

explore = externalFuncs.WinElement(exploreWatch, window=exploreWindow)