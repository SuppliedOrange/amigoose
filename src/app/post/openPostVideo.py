import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs
import vlc
from sys import platform as PLATFORM

player = None

def openPostVideoWindow(videoPath, parent=None):
    global player
    player = vlc.MediaPlayer(videoPath)
    
    videoBasename = externalFuncs.getBasename(videoPath)
    back_button = externalFuncs.getButton("back_button")
    playpause_button = externalFuncs.getButton("playpause")
    buttonColor = externalFuncs.getThemeBackground()
    userDB = externalFuncs.initUserDB()

    sg.theme(externalFuncs.getTheme())

    openPostVideoLayout = [
        [sg.Button(image_filename=back_button, image_subsample=12, button_color= buttonColor, border_width=0, key="openPostVideoClose_" + videoBasename)],
        [sg.Image('', size=(300, 170), key='videoStreamOutput')],
        [sg.Push(),
         sg.Button(image_filename=playpause_button, image_subsample=12, button_color= buttonColor, border_width=0, key="openPostVideoPlayPause_" + videoBasename),
         sg.Push()]
    ]

    window = sg.Window(externalFuncs.getBasename("Viewing a video post"), openPostVideoLayout.copy(), resizable=True, alpha_channel=userDB["settings"].getPreference("opacity"),icon=imageFuncs.getLogo(), metadata={
        "parent": parent,
        "videoBasename": videoBasename
    })

    window.finalize()
    window['videoStreamOutput'].expand(True, True) 

    # Terribly sorry about this Mac users but perhaps try getting a better computer for a lesser cost?
    # Apple doesn't like it when you try and do cool things like play videos on vlc with python
    if PLATFORM.startswith('linux'):
        player.set_xwindow(window['videoStreamOutput'].Widget.winfo_id())
    else:
        player.set_hwnd(window['videoStreamOutput'].Widget.winfo_id())
    
    player.play()

    return window

def openPostVideoWatch(window):
    global player
    
    event,values = window.read(100)

    if(event==sg.WIN_CLOSED):
        window.close()
        player.stop()
        return (True,True) # break, no failure

    if (event == "openPostVideoClose_" + window.metadata["videoBasename"]):
        window.close()
        from src.func.parentHandler import parentHandler
        if window.metadata["parent"]: parentHandler(window.metadata["parent"])
        return (True,True) # break, no failure
    
    if (event == "openPostVideoPlayPause_" + window.metadata["videoBasename"]):
        player.pause()
        

openPostVideo = externalFuncs.WinElement(openPostVideoWatch, window=openPostVideoWindow)