import PySimpleGUI as sg
from src.func import externalFuncs

def settingsLayout():

    userDB = externalFuncs.initUserDB()

    isLoginStyleElegant = (userDB["settings"].getGlobal("loginManager","loginStyle") == "Elegant")
    isThemeDark = (userDB["settings"].getPreference("theme") == "DarkGrey8")
    defaultFont = userDB["settings"].getPreference("font")
    back_button = externalFuncs.getPath(f"./assets/amigoose_assets/back_button_{'light' if isThemeDark else 'dark'}.png")
    edit_button = externalFuncs.getPath(f"./assets/amigoose_assets/edit_{'light' if isThemeDark else 'dark'}.png")

    sg.theme(userDB["settings"].getPreference("theme"))

    settingsLayout = [
        [sg.Button(image_filename=back_button, image_subsample=9, button_color= externalFuncs.getThemeBackground(), border_width=0, key="settings_return_home" ), sg.Push(),
         sg.Button(image_filename=edit_button, image_subsample=30, button_color= externalFuncs.getThemeBackground(), border_width=0, key="settings_move_profileManager" )],
        [sg.Text("Settings",font=(defaultFont,40))],
        [sg.T('')],
        [sg.Text("Choose the GUI's accent"), sg.Push(), sg.Text("Set window opacity [Fun]")],
        [sg.Radio('Dark', "settings_theme", default = isThemeDark, size=(10,1), k='settings_theme_dark'), sg.Radio('Light', "settings_theme", default = not isThemeDark, size=(10,1), k='settings_theme_light'),
         sg.Push(),
         sg.Slider(range=(7,10), default_value=userDB["settings"].getPreference("opacity")*10, size=(20,15), orientation="horizontal", font=(defaultFont,12), key="settings_opacity")
        ],
        [sg.T('')],
        [sg.Text("Select a custom login window style")],
        [sg.Radio('Elegant', 'settings_loginstyle', default = isLoginStyleElegant, size=(10,1), k='settings_loginstyle_elegant'), sg.Radio('Hyper Glow', 'settings_loginstyle', default = not isLoginStyleElegant, size=(10,1), k='settings_loginstyle_hyperglow')],
        [sg.T('')],
        [sg.Text("Choose a custom font | Current:"), sg.Text(defaultFont,text_color= "yellow" if isThemeDark else "blue")],
        [sg.Combo(externalFuncs.getFonts(),key="settings_change_font",default_value=defaultFont)],
        [sg.T('')],
        [sg.Button("Apply Settings", k="settings_apply")],
        [sg.Text("",text_color="red",k="settings_toast_message")],
        [sg.Button("Logout",button_color="red",key="settings_logout")],
        [sg.Button("Developer", button_color="red",key="settings_open_developer_window")],
    ]
    return settingsLayout

def settingsExec(event,values,window):
    if (event == "settings_logout"):
        conf = sg.popup_yes_no("Are you sure you want to logout?")
        if conf == "Yes":
            from src.app.login.logout import logout
            logout()
            exit(0)

    elif (event == "settings_apply"):
        checkAndApply(values,window)

    elif (event == "settings_return_home"):
        externalFuncs.moveTab(window,"tabgroup","settingsTab","homeTab")

    elif (event == "settings_move_profileManager"):
        externalFuncs.moveTab(window, "tabgroup", "settingsTab", "profileManagerTab")

    elif (event == "settings_open_developer_window"):
        from src.app.settings.developerOptions.developerOptions import developerOptions
        developerOptions.start(argsWatch=window)

            

def checkAndApply(values,window):

    userDB = externalFuncs.initUserDB()

    isLoginStyleElegant = (userDB["settings"].getGlobal("loginManager","loginStyle") == "Elegant")
    isThemeDark = (userDB["settings"].getPreference("theme") == "DarkGrey8")

    # Update theme
    if (values['settings_theme_dark'] and not isThemeDark or values['settings_theme_light'] and isThemeDark):
        # Is dark mode selected and is it currently not dark theme? OR Is light mode selected and is it currently dark theme?
        userDB["settings"].updatePreference("theme", "reddit" if values['settings_theme_light'] else "DarkGrey8")
    
    # Update login style
    if (values['settings_loginstyle_elegant'] and not isLoginStyleElegant or values['settings_loginstyle_hyperglow'] and isLoginStyleElegant):
        # Is Elegant selected and is it currently not Elegant login style? OR Is Hyper Glow selected and is it currently Elegant login style?
        userDB["settings"].updateGlobal("loginManager", "loginStyle", "HyperGlow" if isLoginStyleElegant else "Elegant")

    # Update app font
    if (values["settings_change_font"] != userDB["settings"].getPreference("font")):
        userDB["settings"].updatePreference("font",values["settings_change_font"])
    
    # Update window opacity
    # P.S, you might want to delete this in the release, this was just for fun :)
    if (values["settings_opacity"]/10 != userDB["settings"].getPreference("opacity")):
        userDB["settings"].updatePreference("opacity", float(values["settings_opacity"]/10))

    #window["settings_toast_message"].update("Changes applied! Restart the app for changes to take place.")
    from src.app.home.home import home
    home.stop(restart=True)



settings = externalFuncs.TabElement(exec=settingsExec,layout=settingsLayout)