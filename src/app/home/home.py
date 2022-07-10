import PySimpleGUI as sg
from src.func import externalFuncs,imageFuncs
from src.dbfunc import sqlfunc,fixData
fixData.fixData()

from src.app.settings import settings, profileManager
from src.app.home.homeLayoutGenerator import hlg
from src.app.debug import debug

username = sqlfunc.existingUser()

def homeWindow():
    width, height = sg.Window.get_screen_size()
    height,width = int(height/1.2), int(width/1.2)
    
    sg.theme(externalFuncs.getTheme())

    tabs = [
        sg.Tab("Home",hlg.getLayout(),key='homeTab'),
        sg.Tab("Settings",settings.settings.getLayout(),key='settingsTab'),
        sg.Tab("ProfileManager", profileManager.profileManager.getLayout(), key='profileManagerTab'),
        sg.Tab("Debugger", debug.debug.getLayout(), key="debugTab")
    ]

    layout = [[sg.TabGroup([tabs], key='tabgroup', expand_x=True, expand_y=True)]]
    window = sg.Window("Amigoose", layout.copy(),size=(width,height),
                        resizable=True, alpha_channel=externalFuncs.getWindowOpacity(), icon=imageFuncs.getLogo(),
                        right_click_menu=['',['Refresh']], right_click_menu_font=externalFuncs.getDefaultFont(),
                        metadata={
                            "tabs": list(map(lambda x: x.Key ,tabs))
                        })
    window.finalize()
    for tab in window.metadata["tabs"]:
        if tab != "homeTab": externalFuncs.deselectTab(window,tab)
    return window

def homeWatch(window):
    event,values = window.read(50)

    if not event == sg.TIMEOUT_KEY:
    
        if(event==sg.WIN_CLOSED):
            window.close()
            return (True, False) # break, failure

        if (event == "Refresh"):
            home.stop(restart=True)

        v = (event,values,window)

        settings.settings.exec(*v)
        profileManager.profileManager.exec(*v)
        hlg.exec(*v)
        debug.debug.exec(*v)

home = externalFuncs.WinElement(homeWatch,window=homeWindow)