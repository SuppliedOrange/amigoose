import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs
from random import choice

def createSubredditWindow():
    width, height = [int(x/2) for x in sg.Window.get_screen_size()]
    height = int(height * 1.3)
    defaultFont = externalFuncs.getDefaultFont()
    isThemeDark = externalFuncs.isThemeDark()
    back_button = externalFuncs.getButton("back_button")
    sg.theme(externalFuncs.getTheme())
    buttonColor = ("white" if isThemeDark else "black", sg.theme_background_color())

    defaultIconChoices = ["travel","coding","pizza","goose","joystick"]
    defaultIconPath = externalFuncs.getPath(f"./assets/amigoose_assets/{choice(defaultIconChoices)}.png")
    defaultIcon = imageFuncs.convertToB64(imageFuncs.convertToPFP(defaultIconPath, (512,512)))
    

    createSubredditLayout = [
        [sg.Button(image_filename=back_button, image_subsample=9, button_color= buttonColor, border_width=0, key="createSubreddit_close_window" )],
        [sg.T("Create a Gaggle", font=(defaultFont,20))],
        [sg.T()],
        [sg.Button(image_data=defaultIcon, image_subsample=3, button_color= buttonColor, border_width=0, key="createSubreddit_change_icon", metadata=defaultIconPath), sg.Push(),
         sg.Button("MyGaggle", key="createSubreddit_change_name",font=(defaultFont, 30), button_color= buttonColor, border_width=0)],
        [sg.T()],
        [sg.Multiline("Describe your Gaggle",size=(80,8),key="createSubreddit_description")],
        [sg.T()],
        [sg.InputText("Tags for your Gaggle. Ex: gaming,golfing,formula 1,masterchef", key="createSubreddit_tags"),sg.Push(), sg.Button("Create Gaggle!", key="createSubreddit_create_subreddit")],
        [sg.T()],
        [sg.Text(text_color="red",key="createSubreddit_alert")]
    ]

    window = sg.Window("Amigoose - find", createSubredditLayout.copy(),size=(width,height), resizable=True, icon=imageFuncs.getLogo())
    window.finalize()
    return window

def createSubredditWatch(window):
    event,values = window.read(100)

    if(event==sg.WIN_CLOSED or event == "createSubreddit_close_window"):
        window.close()
        return (True,True) # break, no failure
    
    elif (event == "createSubreddit_change_icon"):
        fileName = sg.popup_get_file("Choose an icon",no_window=True)
        if not imageFuncs.checkImage(fileName):
            sg.popup_quick_message("Not an image file! Honk!")
        else:
            newImage = externalFuncs.getPath(fileName)
            window[event].update( image_data=imageFuncs.convertToB64(imageFuncs.convertToPFP(newImage, (200,200))) )
            window[event].metadata = newImage
            sg.popup_quick_message("Updated Gaggle icon!")
    
    elif (event == "createSubreddit_change_name"):
        subredditName = sg.popup_get_text("A name for your Gaggle")
        valid = externalFuncs.subredditNameValidator(subredditName or "mygaggle")
        if not valid[0]:
            window["createSubreddit_alert"].update(valid[1])
        else:
            window[event].update(subredditName)

    elif (event == "createSubreddit_create_subreddit"):
        name = window["createSubreddit_change_name"].get_text()
        description = values["createSubreddit_description"]
        iconpath = window["createSubreddit_change_icon"].metadata

        if (len(description) < 1 or len(description) > 250):
            window["createSubreddit_alert"].update("Your Gaggle's description must be 1-250 characters long.")

        elif name.lower() == "mygaggle":
            window["createSubreddit_alert"].update("Did you forget to set a name for your Gaggle?")

        else:
            # Setting the subreddit icon
            imageFuncs.saveAsPFP(iconpath, name, subreddit=True)
            # There is a better way to do this. We can assign metadata to the subreddit name to use the default amigoose asset if there is no custom subreddit icon. 
            # However considering that this is simply easier to do and maintain, I won't bother complicating it.

            # Creating the actual subreddit
            userDB = externalFuncs.initUserDB()
            userDB["postData"].makeSubreddit(name,description)

            # Appending subreddit to global tags
            tags = values["createSubreddit_tags"]
            if tags and tags != "Tags for your Gaggle. Ex: gaming,golfing,formula 1,masterchef":
                tags = list(tag.strip() for tag in tags.split(","))
                from src.dbfunc.jsonfunc import loadData,updateFile
                gtags = loadData()
                for tag in tags:
                    if tag in gtags:
                        gtags[tag].append(name)
                    else:
                        gtags[tag] = [name]
                updateFile(gtags)
                

            # Now you'll need to open the subreddit. Need to build that.
            window.close()
            return (True,True)

createSubreddit = externalFuncs.WinElement(createSubredditWatch, window=createSubredditWindow)