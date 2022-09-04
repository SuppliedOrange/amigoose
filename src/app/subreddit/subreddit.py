from ast import NameConstant
import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs, parentHandler
from datetime import datetime

from . import top, new

def subredditWindow(subreddit,openTab=None,parent=None):
    if not externalFuncs.isSubreddit(subreddit):
        raise SubredditNotFound(f"Subreddit {subreddit} does not exist")

    width, height = [int(x/1.5) for x in sg.Window.get_screen_size()]
    openTab = openTab or "subredditTab"
    defaultFont = externalFuncs.getDefaultFont()
    back_button = externalFuncs.getButton("back_button")
    buttonColor = ("white" if externalFuncs.isThemeDark() else "black", sg.theme_background_color())

    userDB = externalFuncs.initUserDB()
    icon = imageFuncs.convertToPFP( imageFuncs.getIcon(subreddit) ,(200,200), cacheOutput=(subreddit, "subreddit"))
    date_created = datetime.utcfromtimestamp( userDB["postData"].getSubreddits(subreddit, "dateCreated")[0] ).strftime("%d/%m/%Y")
    owner = userDB["postData"].getSubreddits(subreddit, "owner")[0]
    description = userDB["postData"].getSubreddits(subreddit, "description")[0]
    members = userDB["userData"].getSubredditMembers(subreddit)[0]

    sg.theme(externalFuncs.getTheme())

    isNotOwner = (userDB["dataTables"].username != owner)

    # If the user is not the owner of the subreddit, load an image of the subreddit icon for them, otherwise load a button with the subreddit icon
    iconButton = sg.Image(filename=icon) if isNotOwner else sg.Button(image_filename=icon,button_color=buttonColor, border_width=0, key="subreddit_update_icon-" + subreddit)
    # Header = [iconButton/iconImage + push + subreddit name]
    header = [iconButton, sg.Push(), sg.Text("g/" + subreddit, font=(defaultFont,40))]

    # The description is going to be a multiline element, where if the user is not an owner, the multiline is disabled.
    subreddit_info = [ sg.Multiline(description,disabled=isNotOwner, font=(defaultFont,10), size=(50, 20), background_color="gray" if externalFuncs.isThemeDark() else "white", border_width=0), ]
    description = [sg.Frame("About", [subreddit_info])]

    if not isNotOwner:
        # If the user is the owner, give them a special update button to change the subreddit description.
        description.append( sg.Button("Update", key="subreddit_update_description-" + subreddit) )
        description.append( sg.Push() )

    details = [
        [sg.Text("Members:" + str(members),font=(defaultFont,15))],
        [sg.Button("By @" + owner, button_color=buttonColor,border_width=0,font=(defaultFont,15), key="subreddit_open_profile-" + owner)],
        [sg.Text("On " + date_created,font=(defaultFont,15))]
    ]
    description.append(sg.Frame("", details, element_justification="c"))

    subredditLayout = [
        [sg.Button(image_filename=back_button, image_subsample=9, button_color= buttonColor, border_width=0, key="subreddit_return_home-" + subreddit ),
         sg.Push(),
         sg.Button("new", font=(defaultFont,28), button_color=buttonColor, border_width=0, key="subreddit_open_new-" + subreddit), sg.Button("top", font=(defaultFont,28), button_color = buttonColor, border_width=0, key="subreddit_open_top-" + subreddit)],
        header,
        [sg.T()],
        description
    ]

    tabs = [
        sg.Tab("g/" + subreddit, subredditLayout, key="subredditTab"),
        sg.Tab("g/" + subreddit, top.top.getLayout(subreddit), key="topTab"),
        sg.Tab("g/" + subreddit, new.new.getLayout(subreddit), key="newTab")
    ]

    subredditLayout = [[sg.TabGroup([tabs], key='subredditTabgroup', expand_x=True, expand_y=True)]]
    window = sg.Window("g/" + subreddit , subredditLayout.copy(),size=(width,height), resizable=True, alpha_channel=externalFuncs.getWindowOpacity(), icon=imageFuncs.getLogo(), metadata={
        "tabs": list(map(lambda x: x.Key ,tabs)),
        "subreddit": subreddit,
        "parent": parent
    })

    window.finalize()
    for tab in window.metadata["tabs"]:
        if tab != openTab: externalFuncs.deselectTab(window,tab)
    return window

def subredditWatch(window):

    if type(window) == tuple and not window[0]:
        raise Exception
    
    event,values = window.read(100)
    event = externalFuncs.sanitizeEvent(event)

    method,value = event.split("-") if event and "-" in event else (None,None)

    if value == window.metadata["subreddit"]:
        event = method

    # Standard events (directly linked to subreddit)

    if(event==sg.WIN_CLOSED):
        window.close()
        return (True,True) # break, no failure
    
    if (event == "subreddit_return_home"):
        window.close()
        if window.metadata["parent"]: parentHandler.parentHandler(window.metadata["parent"])
        return (True,True)
    
    elif (event == "subreddit_open_new"):
        externalFuncs.moveTab(window, "subredditTabgroup", "subredditTab", "newTab")
    
    elif (event == "subreddit_open_top"):
        externalFuncs.moveTab(window, "subredditTabgroup", "subredditTab", "topTab")

    elif (event == "subreddit_update_icon"):
        fileName = sg.popup_get_file("Choose a subreddit icon",no_window=True)
        if not imageFuncs.checkImage(fileName):
            sg.popup_quick_message("Not an image file! Honk!")
        else:
            newPFP = imageFuncs.convertToPFP(imageFuncs.saveAsPFP(fileName, window.metadata["subreddit"], subreddit=True), (200,200), cacheOutput=(subreddit, "subreddit"))
            window[event + "-" + window.metadata["subreddit"]].update(image_data=imageFuncs.convertToB64(newPFP))
            sg.popup_quick_message("Updated subreddit icon!")

    # Events where we call external windows

    elif (method == "subreddit_open_profile"):
        #subredit, openTab, parent - subreddit args
        parent = {"type": "subreddit", "layoutArgs": (window.metadata["subreddit"], None, window.metadata["parent"])}
        # username, openTab, parent - profile args
        username  = event.split("-")[1]
        profileLayoutArgs = (username, None, parent)
        from src.app.profile.profile import profile
        window.close()
        profile.start(argsWindow=profileLayoutArgs)
        return (True, True) # Might be problematic, wanna test.
    
    elif (event in ("subreddit+top_add_post","subreddit+new_add_post")):
        # Find out where the event came from
        returnToTab = "topTab" if event == "subreddit+top_add_post" else "newTab"
        # subreddit, openTab, parent - subreddit args
        parent = {"type": "subreddit", "layoutArgs": (window.metadata["subreddit"], returnToTab, window.metadata["parent"])}
        # existingTitle, parent - createPostTitle args
        createPostTitleArgs = (window.metadata["subreddit"],None,parent)
        from src.app.post.createPost.createPostTitle import createPostTitle
        window.close()
        createPostTitle.start(argsWindow=createPostTitleArgs)
        return (True, True)

    v = (event,values,window)

    top.top.exec(*v)
    new.new.exec(*v)

subreddit = externalFuncs.WinElement(subredditWatch, window=subredditWindow)

class SubredditNotFound(Exception):
    pass