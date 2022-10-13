import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs
from src.func.layoutParser import getSubredditsForUser

def profileManagerLayout():

    userDB = externalFuncs.initUserDB()
    
    defaultFont = externalFuncs.getDefaultFont()
    back_button = externalFuncs.getButton("back_button")
    modify_button = externalFuncs.getButton("edit")
    wrench_button = externalFuncs.getButton("wrench")
    add_button = externalFuncs.getButton("add")
    buttonColor = externalFuncs.getThemeBackground()
    bio = userDB["userData"].getProfileData("bio")[0]
    pfp = imageFuncs.convertToPFP(imageFuncs.getPFP(userDB["dataTables"].username), (200,200))
    pfp = imageFuncs.convertToB64(pfp)
    width, height = [int(x/3) for x in sg.Window.get_screen_size()]

    sg.theme(externalFuncs.getTheme())

    profileManagerLayout = [
        [sg.Button(image_filename=back_button, image_subsample=9, button_color= externalFuncs.getThemeBackground(), border_width=0, key="profileManager_return_home"), sg.Push(),
         sg.Button(image_filename=wrench_button, image_subsample=4, button_color= externalFuncs.getThemeBackground(), border_width=0, key="profileManager_move_settings")],
        [sg.Text("Edit Profile",font=(defaultFont,40))],
        [sg.T('\n')],
        [sg.Image(data = pfp, k='profileManager_pfp'), sg.Button(image_filename=modify_button, image_subsample=35, button_color= buttonColor, border_width=0, key="profileManager_edit_pfp"),
        sg.Push(),
        sg.Text(f"\"{bio}\"" if bio else "Write something about yourself", font=(defaultFont,12), size=(int(width/17), int(height/40)), key="profileManager_bio"),
        sg.Push(),
        sg.Button(image_filename=modify_button, image_subsample=35, button_color= buttonColor, border_width=0, key="profileManager_edit_username"), sg.Text(userDB["dataTables"].username, font=(defaultFont,40), k='profileManager_username')],
        [sg.Push(), sg.Button(image_filename=modify_button, image_subsample=35, button_color= buttonColor, border_width=0, key="profileManager_edit_bio"), sg.Push()],
        [sg.T("Gaggles",font=(defaultFont,20)), sg.Button(image_filename=add_button,image_subsample=16,button_color= buttonColor, border_width=0, key="profileManager_create_subreddit"),
         sg.Push(),
         sg.T("Blocked", font=(defaultFont,20)), sg.Button(image_filename=add_button,image_subsample=16,button_color= buttonColor, border_width=0,key="profileManager_block_user")],
        [
        *getSubredditsForUser(userDB["dataTables"].username),
        sg.Push(),
        sg.Column([], scrollable=True, vertical_scroll_only=True, size=(width,height), sbar_relief=sg.RELIEF_FLAT),
        ],
    ]
    return profileManagerLayout

def profileManagerExec(event,values,window):
    if (event == "profileManager_return_home"):
        externalFuncs.moveTab(window,"tabgroup","profileManagerTab","homeTab")
    elif (event == "profileManager_move_settings"):
        externalFuncs.moveTab(window, "tabgroup", "profileManagerTab", "settingsTab")
    elif (event == "profileManager_edit_pfp"):
        fileName = sg.popup_get_file("Choose a profile image",no_window=True,icon=imageFuncs.getLogo("light"))
        if not imageFuncs.checkImage(fileName):
            sg.popup_quick_message("Not an image file! Honk!")
        else:
            username = externalFuncs.initUserDB()["dataTables"].username
            newPFP = imageFuncs.convertToPFP(imageFuncs.saveAsPFP(fileName, username), (200,200), cacheOutput=(username, "user"))
            window["profileManager_pfp"].update(data=imageFuncs.convertToB64(newPFP))
            sg.popup_quick_message("Updated profile picture!")
    elif (event == "profileManager_edit_username"):
        changeUsernameWindow()
    elif (event == "profileManager_edit_bio"):
        changeBioWindow(window)
    elif (event == "profileManager_create_subreddit"):
        from src.app.settings.createSubreddit.createSubreddit import createSubreddit
        createSubreddit.start()
    elif (event == "profileManager_block_user"):
        from src.app.settings.blockUser.blockUser import blockUser
        blockUser.start()

    if ("-" in event):
        method,value = event.split("-")[0], event.split("-")[1]
        if (method == "leave_subreddit"):
            conf = sg.popup_yes_no("Are you sure you want to leave g/" + value + "?")
            if conf == "Yes":
                userDB = externalFuncs.initUserDB()
                userDB["userData"].leaveSubreddit(value)
                window[event].update("Left", disabled=True)
        elif (method == "delete_subreddit"):
            conf = sg.popup_yes_no("Are you sure you want to delete g/" + value + "?")
            if conf == "Yes":
                userDB = externalFuncs.initUserDB()
                userDB["postData"].deleteSubreddit(value)
                window[event].update("Deleted", disabled=True)


def changeUsernameWindow():
    userDB = externalFuncs.initUserDB()
    defaultFont = userDB["settings"].getPreference("font")
    changeUsernameLayout = [
        [sg.Text("Change username", font=(defaultFont,20))],
        [sg.InputText(k="newUsername")],
        [sg.Text(text_color="red",k="toast")],
        [sg.Button("Change",disabled=True,k="confirm")]
    ]
    window = sg.Window("Amigoose - Change username", layout= changeUsernameLayout.copy(), element_justification="c",margins=(0,0),element_padding=(0,0),finalize=True, auto_size_text=True,keep_on_top=True,modal=True,icon=imageFuncs.getLogo(),alpha_channel=externalFuncs.getWindowOpacity())
    window.make_modal()

    from src.crypto.encryptor import usernameValidator

    while True:
        event, values = window.read(timeout=100)
        if event in (sg.WIN_CLOSED, None):
            break
        
        vUsername = usernameValidator(values["newUsername"])
        if not vUsername[0]:
            window["toast"].update(vUsername[1], text_color="red")
            window["confirm"].update(disabled=True)
        else:
            window["toast"].update("Valid Username", text_color="blue")
            window["confirm"].update(disabled=False)

        if (event == "confirm"):
            nu = values["newUsername"]
            window.close()
            conf = sg.popup_yes_no("Are you sure you want to change your username to " + nu + "?\nThe app will close after this.")
            if conf != "Yes": break

            # Changing the username
            userDB["userData"].changeUsername(nu)

            # Updating the profile picture's name
            from src.func import imageFuncs as imf
            userPFP = imf.getPFP(userDB["dataTables"].username)
            if userPFP:
                import os
                newUserPFP = externalFuncs.getPath("./assets/user_assets/pfps/" + nu.lower() + ".png")
                os.rename(userPFP.lower(),newUserPFP.lower())
            from src.app.home.home import home
            home.stop()
            window.close()
            break

def changeBioWindow(parentWindow):
    userDB = externalFuncs.initUserDB()
    bio = userDB["userData"].getProfileData("bio")[0]
    defaultFont = userDB["settings"].getPreference("font")
    changeUsernameLayout = [
        [sg.Text("Change Biography", font=(defaultFont,20))],
        [sg.Multiline(bio if bio else "Write a honkin' good Bio for yourself!",size=(50,10),k="newBio")],
        [sg.Text(text_color="red",k="toast")],
        [sg.Button("Update Bio",disabled=True,k="confirm")]
    ]
    window = sg.Window("Amigoose - Change Bio", layout= changeUsernameLayout.copy(), element_justification="c",margins=(0,0),element_padding=(0,0),finalize=True, auto_size_text=True,keep_on_top=True,modal=True,icon=imageFuncs.getLogo(),alpha_channel=externalFuncs.getWindowOpacity())
    window.make_modal()

    while True:
        event, values = window.read(timeout=100)
        if event in (sg.WIN_CLOSED, None):
            break
        
        if len(values["newBio"]) > 150:
            window["toast"].update(f"{len(values['newBio'])}/150", text_color="red")
            window["confirm"].update(disabled=True)
        else:
            window["toast"].update(f"{len(values['newBio'])}/150", text_color="blue")
            window["confirm"].update(disabled=False)

        if (event == "confirm"):
            nb = values["newBio"]
            userDB["userData"].updateProfileData("bio",nb)
            parentWindow["profileManager_bio"].update(f"\"{nb}\"" if nb else "Write something about yourself")
            window.close()
            break

profileManager = externalFuncs.TabElement(exec=profileManagerExec,layout=profileManagerLayout)