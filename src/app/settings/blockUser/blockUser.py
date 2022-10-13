import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs
from src.dbfunc import csvfunc, sqlfunc

prediction_list, input_text, sel_item, list_element, choices = [], "", 0, None, []
sqlfunc.selectDB("userdata")
allUsers = sqlfunc.loadColumn("profiledata", "username")

def blockUserWindow():
    global prediction_list, input_text, sel_item, list_element, choices
    prediction_list, input_text, sel_item = [], "", 0

    width, height = [int(x/3) for x in sg.Window.get_screen_size()]
    choices = []
    inputWidth = 40
    itemCap = 4

    defaultFont = externalFuncs.getDefaultFont()
    back_button = externalFuncs.getButton("back_button")
    confirm_button = externalFuncs.getButton("confirm")
    buttonColor = externalFuncs.getThemeBackground()
    userDB = externalFuncs.initUserDB()

    sg.theme(externalFuncs.getTheme())

    blockUserLayout = [
        [sg.Button(image_filename=back_button, image_subsample=9, button_color= buttonColor, border_width=0, key="blockUser_return_home")],
        [sg.Push(), sg.Text('Choose a user to block',justification="c", font=(defaultFont,15)), sg.Push()],
        [sg.Push(), sg.Input(size=(inputWidth, 20), enable_events=True, focus=True, key='blockUser_query'), sg.Push()],
        [sg.Push(), sg.pin(sg.Col([ [sg.Listbox(values=[], size=(inputWidth, itemCap), enable_events=True, key='blockUser_box', select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=True)] ], key='blockUser_box_container', pad=(0, 0), visible=False)), sg.Push()],
        [sg.VPush()], [sg.VPush()],
        [sg.Push(), sg.Button(image_filename=confirm_button, image_subsample=15, button_color= buttonColor, border_width=0, key="blockUser_submit")],
        [sg.VPush()]
    ]

    window = sg.Window("Block user" ,blockUserLayout.copy(),size=(width,height), resizable=True, alpha_channel=userDB["settings"].getPreference("opacity"),icon=imageFuncs.getLogo())
    list_element = window.Element('blockUser_box')
    window.finalize()
    window["blockUser_query"].bind("<Down>","-pressed_down")
    window["blockUser_query"].bind("<Up>","-pressed_up")
    window["blockUser_query"].bind("<Return>","-pressed_enter")
    return window

def blockUserWatch(window):
    global prediction_list, input_text, sel_item, list_element, choices
    
    event,values = window.read(100)
    event = externalFuncs.sanitizeEvent(event)

    choices = getMatchingUsers(values['blockUser_query']) if values else []

    method, value = None,None

    if event and len(event.split("-")) > 1:
        method, value = event.split("-")

    if(event==sg.WIN_CLOSED or event == "blockUser_return_home"):
        window.close()
        return (True,True) # break, no failure

    elif value == "pressed_down" and len(prediction_list): # Down arrow key pressed
        sel_item = (sel_item + 1) % len(prediction_list)
        list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)

    elif value == "pressed_up" and len(prediction_list): # Up arrow key pressed
        sel_item = (sel_item + (len(prediction_list) - 1)) % len(prediction_list)
        list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)

    elif value == "pressed_enter": # Enter key pressed
        if len(prediction_list): # If prediction list is active
            if len(values['blockUser_box']) > 0:
                chosenSubreddit = values['blockUser_box'][0]
                if chosenSubreddit[0] == "@": chosenSubreddit = chosenSubreddit[1::]
                window['blockUser_query'].update(value=[chosenSubreddit][0])
                window['blockUser_box_container'].update(visible=False)
                prediction_list = []
        else:
            window["blockUser_submit"].Click()

    elif event == 'blockUser_query':
        text = values['blockUser_query'].lower().strip()
        if text != input_text:
            input_text = text
            prediction_list = []
            if text:
                prediction_list = ["@" + item for item in choices if item.lower().strip().startswith(text)]

            list_element.update(values=prediction_list)
            sel_item = 0
            list_element.update(set_to_index=sel_item)

            if len(prediction_list) > 0:
                window['blockUser_box_container'].update(visible=True)
            else:
                window['blockUser_box_container'].update(visible=False)

    elif event == 'blockUser_box':
        chosenUser = values['blockUser_box'][0]
        if chosenUser[0] == "@": chosenSubreddit = chosenSubreddit[1::]
        window['blockUser_query'].update(value=[chosenSubreddit][0])
        window['blockUser_box_container'].update(visible=False)

    elif event == "blockUser_submit":
        legal = True
        target = values["blockUser_query"].strip().lower()
        if not target:
            sg.popup_non_blocking("You aren't searching for anything!")
        elif not target in allUsers:
            sg.popup_non_blocking("That's not a valid username!")
        else:
            #csvfunc.addBlock(sqlfunc.existingUser(), target)
            sg.popup_non_blocking("Hold on! I haven't finished the layout. I can't add this yet.")

blockUser = externalFuncs.WinElement(blockUserWatch, window=blockUserWindow)

def getMatchingUsers(query):
    blockedUserList = csvfunc.getBlockedUsersFor(sqlfunc.existingUser())
    allUsers, blockedUserList = [x.lower() for x in allUsers], [x.lower() for x in blockedUserList]
    allUsers = [x for x in allUsers if x not in blockedUserList and x != sqlfunc.existingUser().lower()]
    return [x for x in allUsers if query and x.startswith(query)]