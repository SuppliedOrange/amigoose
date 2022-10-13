import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs
from src.dbfunc import sqlfunc

prediction_list, input_text, sel_item, list_element, choices = [], "", 0, None, []

def opensubWindow():
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

    opensubLayout = [
        [sg.Button(image_filename=back_button, image_subsample=9, button_color= buttonColor, border_width=0, key="opensub_return_home")],
        [sg.Push(), sg.Text('Find a gaggle by name',justification="c", font=(defaultFont,15)), sg.Push()],
        [sg.Push(), sg.Input(size=(inputWidth, 20), enable_events=True, focus=True, key='opensub_query'), sg.Push()],
        [sg.Push(), sg.pin(sg.Col([ [sg.Listbox(values=[], size=(inputWidth, itemCap), enable_events=True, key='opensub_box', select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=True)] ], key='opensub_box_container', pad=(0, 0), visible=False)), sg.Push()],
        [sg.VPush()], [sg.VPush()],
        [sg.Push(), sg.Button(image_filename=confirm_button, image_subsample=15, button_color= buttonColor, border_width=0, key="opensub_submit")],
        [sg.VPush()]
    ]

    window = sg.Window("Open Gaggle" ,opensubLayout.copy(),size=(width,height), resizable=True, alpha_channel=userDB["settings"].getPreference("opacity"),icon=imageFuncs.getLogo())
    list_element = window.Element('opensub_box')
    window.finalize()
    window["opensub_query"].bind("<Down>","-pressed_down")
    window["opensub_query"].bind("<Up>","-pressed_up")
    window["opensub_query"].bind("<Return>","-pressed_enter")
    return window

def opensubWatch(window):
    global prediction_list, input_text, sel_item, list_element, choices
    
    event,values = window.read(100)
    event = externalFuncs.sanitizeEvent(event)

    choices = getMatchingSubreddits(values['opensub_query']) if values else []

    method, value = None,None

    if event and len(event.split("-")) > 1:
        method, value = event.split("-")

    if(event==sg.WIN_CLOSED or event == "opensub_return_home"):
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
            if len(values['opensub_box']) > 0:
                chosenSubreddit = values['opensub_box'][0]
                if chosenSubreddit[0:2] == "g/": chosenSubreddit = chosenSubreddit[2::]
                window['opensub_query'].update(value=[chosenSubreddit][0])
                window['opensub_box_container'].update(visible=False)
                prediction_list = []
        else:
            window["opensub_submit"].Click()

    elif event == 'opensub_query':
        text = values['opensub_query'].lower().strip()
        if text != input_text:
            input_text = text
            prediction_list = []
            if text:
                prediction_list = ["g/" + item for item in choices if item.lower().strip().startswith(text)]

            list_element.update(values=prediction_list)
            sel_item = 0
            list_element.update(set_to_index=sel_item)

            if len(prediction_list) > 0:
                window['opensub_box_container'].update(visible=True)
            else:
                window['opensub_box_container'].update(visible=False)

    elif event == 'opensub_box':
        chosenSubreddit = values['opensub_box'][0]
        if chosenSubreddit[0:2] == "g/": chosenSubreddit = chosenSubreddit[2::]
        window['opensub_query'].update(value=[chosenSubreddit][0])
        window['opensub_box_container'].update(visible=False)

    elif event == "opensub_submit":
        subredditName = values["opensub_query"].strip()
        if (externalFuncs.isSubreddit(subredditName)):
            window.close()
            from src.app.subreddit.subreddit import subreddit
            subreddit.start(argsWindow=subredditName)
            return (True, True)

opensub = externalFuncs.WinElement(opensubWatch, window=opensubWindow)

def getMatchingSubreddits(query):
    sqlfunc.selectDB("postData")
    return list(sqlfunc.searchData("subreddits","name",query,fetchAll=True))[0:6]
