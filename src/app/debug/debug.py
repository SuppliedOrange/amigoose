import PySimpleGUI as sg
from src.func import externalFuncs
from .logger import log,now

def debugLayout():
    defaultFont = externalFuncs.getDefaultFont()
    back_button = externalFuncs.getButton("back_button")
    sg.theme(externalFuncs.getTheme())
    buttonColor = externalFuncs.getThemeBackground()

    debugLayout = [
        [sg.Button(image_filename=back_button, image_subsample=9, button_color= buttonColor, border_width=0, key="debug_return_settings")],
        [sg.Push(), sg.Text("Debugger",font=(defaultFont,40),justification="c"), sg.Push()],
        [sg.Push(), sg.Multiline(size=(90,70),autoscroll=True,key="debuggerConsole",horizontal_scroll=True,auto_refresh=True), sg.Push()]
    ]

    return debugLayout

def debugExec(event,values,window):

    if event == "debug_return_settings":
        externalFuncs.moveTab(window,"tabgroup","debugTab","settingsTab")

    try:
        if event != sg.TIMEOUT_KEY:
            window["debuggerConsole"].update(values["debuggerConsole"] + "\n" + now() + "Event: " + event)
    except:
        exit(0) # After exiting the program, there is a chance that it continues running and logging. It is necessary to exit.

    log(values["debuggerConsole"])
    

debug = externalFuncs.TabElement(layout=debugLayout,exec=debugExec)