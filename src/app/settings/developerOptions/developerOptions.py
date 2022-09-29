import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs

def developerOptionsWindow():
    defaultFont = externalFuncs.getDefaultFont()
    back_button = externalFuncs.getButton("back_button")

    developerOptionsLayout = [
        [sg.Button(image_filename=back_button, image_subsample=9, button_color= externalFuncs.getThemeBackground(), border_width=0, key="developerOptions_close" )],
        [sg.Text("\nDeveloper\n", font=(defaultFont,20))],
        [sg.Button("Reset Amigoose",button_color="red",k="developerOptions_drop_all")],
        [sg.Button("Refresh App", button_color="red", k="developerOptions_refresh_app")],
        [sg.Button("Delete Account", button_color="red",key="developerOptions_delete_user")],
        [sg.Button("Open Debugger", button_color="red",key="developerOptions_open_debugger")]
    ]

    window = sg.Window("Amigoose - Developer Options" ,developerOptionsLayout.copy(), resizable=True, modal=True, alpha_channel=externalFuncs.getWindowOpacity(),icon=imageFuncs.getLogo())
    window.finalize()
    window.make_modal()

    return window

def developerOptionsWatch(window,mainWindow):
    event,values = window.read(100)

    if(event==sg.WIN_CLOSED or event == "developerOptions_close"):
        window.close()
        return (True,True) # break, no failure
    
    elif (event == "developerOptions_refresh_app"):
        from src.app.home.home import home
        window.close()
        home.stop(restart=True)
        return (True,True)

    elif (event == "developerOptions_drop_all"):
        from src.dbfunc import sqlfunc
        from src.app.home.home import home
        conf = sg.popup_yes_no("u sure bro?")
        if conf == "Yes": 
            window.close()
            sqlfunc.dropAll()
            home.stop()
            return (True,True)
    
    elif (event == "developerOptions_open_debugger"):
        window.close()
        externalFuncs.moveTab(mainWindow,"tabgroup","settingsTab","debugTab")
        return (True,True)
    
    elif (event == "developerOptions_delete_user"):
        user = sg.popup_get_text("Greetings, godfather. Whose grave shall I dig?")
        if not externalFuncs.isUser(user):
            sg.popup_quick_message("user " + (user or "*nothing*") + " doesnt exist")
        else:
            from src.dbfunc import sqlfunc as sf
            currUser = sf.existingUser()
            d = sf.deleteAccount(user)
            sg.popup_quick_message(d[1])
            if user == currUser:
                print("and death be to thou!")
                return (True,False)
            window.close()
            sg.popup_quick_message(user + " is no more.")
            return (True,True)
    
developerOptions = externalFuncs.WinElement(developerOptionsWatch, window=developerOptionsWindow)