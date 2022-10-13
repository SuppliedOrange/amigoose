import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs
from src.func.layoutParser import getClosestMatchUsers, getClosestMatchSubreddit

def searchWindow(search_query=""):
    width, height = [int(x/2) for x in sg.Window.get_screen_size()]

    defaultFont = externalFuncs.getDefaultFont()
    isThemeDark = externalFuncs.isThemeDark()
    back_button = externalFuncs.getButton("back_button")
    confirm_button = externalFuncs.getButton("confirm")
    sg.theme(externalFuncs.getTheme())
    buttonColor = externalFuncs.getThemeBackground()

    searchLayout = [
        [sg.Button(image_filename=back_button, image_subsample=9, button_color= externalFuncs.getThemeBackground(), border_width=0, key="search_return_home" )],
        [sg.Text("Search for", font=(defaultFont,35))],
        [sg.InputText(search_query, focus=True, key="search_query")],
        [sg.T('\n')],
        [sg.Text("search",font=(defaultFont, 13)), [sg.Button(image_filename=confirm_button, image_subsample=25, button_color= buttonColor, border_width=0, key="search_everywhere")]],
        #[sg.T()],
        [sg.Text(text_color="yellow" if isThemeDark else "blue",key="search_subreddit_highlight",font=(defaultFont, 13)), [sg.Button(image_filename=confirm_button, image_subsample=25, button_color= buttonColor, border_width=0,visible=False, key="search_open_subreddit")]],
        #[sg.T()],
        [sg.Text(text_color="yellow" if isThemeDark else "blue",key="search_user_highlight",font=(defaultFont, 13)), [sg.Button(image_filename=confirm_button, image_subsample=25, button_color= buttonColor, border_width=0, visible=False, key="search_open_profile")]],
        #[sg.T()],
        [sg.Text(text_color="red", key="search_toast_message",font=(defaultFont, 15))]
    ]

    window = sg.Window("Amigoose - find" , searchLayout.copy(),size=(width,height), resizable=True, alpha_channel=externalFuncs.getWindowOpacity(),icon=imageFuncs.getLogo())
    window.finalize()
    window["search_query"].bind("<Return>","-pressed_enter")
    return window

def searchWatch(window):
    event,values = window.read(100)

    if(event==sg.WIN_CLOSED or event == "search_return_home"):
        window.close()
        return (True,True) # break, no failure

    elif(event == "search_open_profile"):
        window.close()
        from src.app.profile.profile import profile
        profile.start(argsWindow=values["search_query"])
        return (True,True)

    elif (event == "search_open_subreddit"):
        window.close()
        from src.app.subreddit.subreddit import subreddit
        subreddit.start(argsWindow=values["search_query"])
        return (True,True)

    elif (event == "search_everywhere"):

        defaultFont = externalFuncs.getDefaultFont()

        window.close()

        layout = [
            [sg.Button(image_filename=externalFuncs.getButton("back_button"), image_subsample=9, button_color=externalFuncs.getThemeBackground(), border_width=0, key="closeWindow" )],
            [sg.Text("Users:\n",font=(defaultFont,30)), sg.Push(), sg.Text("Gaggles:\n",font=(defaultFont, 30)), sg.Push()],
            [getClosestMatchUsers(values["search_query"]), getClosestMatchSubreddit(values["search_query"])]
        ]
        size = [int(x/2) for x in sg.Window.get_screen_size()]
        Nwindow = sg.Window("Amigoose - Search", layout.copy(),margins=(0,0),element_padding=(0,0),finalize=True,auto_size_text=True, size=size, icon=imageFuncs.getLogo() )


        while True:
            Nevent, Nvalues = Nwindow.read(timeout=100)
            
            if Nevent in (sg.WIN_CLOSED, None, "closeWindow"):
                Nwindow.close()
                break

            if ("-" in Nevent):
                method, value = Nevent.split("-")[0], Nevent.split("-")[1]
                if (method == "search_open_profile"):
                    Nwindow.close()
                    from src.app.profile.profile import profile
                    profile.start(argsWindow=value.lower())
                    break
                elif (method == "search_join_subreddit"):
                    userDB = externalFuncs.initUserDB()
                    userDB["userData"].joinSubreddit(value)
                    Nwindow[Nevent].update("Joined", disabled=True, button_color= ("white","green"))

                elif (method == "search_leave_subreddit"):
                    userDB = externalFuncs.initUserDB()
                    userDB["userData"].leaveSubreddit(value)
                    Nwindow[Nevent].update("Left", disabled=True, button_color = ("white","red"))
                
                elif (method == "search_open_subreddit"):
                    parent = {"type": "search", "layoutArgs": values["search_query"]}
                    subredditLayoutArgs = (value,None,parent)
                    from src.app.subreddit.subreddit import subreddit
                    Nwindow.close()
                    subreddit.start(argsWindow=subredditLayoutArgs)


        return (True,True)
    
    elif ("pressed_enter" in event):
        window["search_everywhere"].Click()
        
    # If user exists, change value to @user and update button
    if (externalFuncs.isUser(values["search_query"])):
        window["search_user_highlight"].update("@" + values["search_query"])
        window["search_open_profile"].update(visible=True)
    else:
        window["search_user_highlight"].update("")
        window["search_open_profile"].update(visible=False)
    
    # If subreddit exists, change value to g/subreddit and update button
    if (externalFuncs.isSubreddit(values["search_query"])):
        window["search_subreddit_highlight"].update("g/" + values["search_query"])
        window["search_open_subreddit"].update(visible=True)
    else:
        window["search_subreddit_highlight"].update("")
        window["search_open_subreddit"].update(visible=False)
    
    if (values["search_query"]):
        if not externalFuncs.checkIllegalInput(values["search_query"]):
            window["search_toast_message"].update("No special symbols! Honk!")
        else:
            window["search_toast_message"].update("")
        

search = externalFuncs.WinElement(searchWatch, window=searchWindow)