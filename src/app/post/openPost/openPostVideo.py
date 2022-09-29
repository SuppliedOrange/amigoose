import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs
import vlc
from sys import platform as PLATFORM

player = None

def openPostVideoWindow(videoPath, parent=None):

    width, height = [int(x/2) for x in sg.Window.get_screen_size()]

    global player
    player = vlc.MediaPlayer(videoPath)
    videoBasename = externalFuncs.getBasename(videoPath)
    back_button = externalFuncs.getButton("back_button")
    playpause_button = externalFuncs.getButton("playpause")
    mute_button = externalFuncs.getButton("mute")
    double_front_arrow_button = externalFuncs.getButton("double_front_arrow")
    double_back_arrow_button = externalFuncs.getButton("double_back_arrow")
    buttonColor = externalFuncs.getThemeBackground()
    userDB = externalFuncs.initUserDB()

    sg.theme(externalFuncs.getTheme())

    openPostVideoLayout = [
        [sg.Button(image_filename=back_button, image_subsample=12, button_color= buttonColor, border_width=0, key="openPostVideoClose_" + videoBasename)],
        [sg.Image('', size=(300, 170), key='videoStreamOutput')],
        [sg.Push(),
         sg.Button(image_filename=double_back_arrow_button, image_subsample=20, button_color= buttonColor, border_width=0, key="openPostVideoBackArrow_" + videoBasename),
         sg.T(),
         sg.Button(image_filename=playpause_button, image_subsample= 10, button_color= buttonColor, border_width=0, key="openPostVideoPlayPause_" + videoBasename),
         sg.T(),
         sg.Button(image_filename=double_front_arrow_button, image_subsample=20, button_color= buttonColor, border_width=0, key="openPostVideoFrontArrow_" + videoBasename),
         sg.Push(),
         sg.Button(image_filename=mute_button, image_subsample=20, button_color=buttonColor, border_width=0, key="openPostVideoMute_" + videoBasename)]
    ]

    window = sg.Window(externalFuncs.getBasename("Viewing a video post"), openPostVideoLayout.copy(), resizable=True, size=(width, height), alpha_channel=userDB["settings"].getPreference("opacity"),icon=imageFuncs.getLogo(), metadata={
        "parent": parent,
        "videoBasename": videoBasename
    })

    window.finalize()
    window['videoStreamOutput'].expand(True, True) 

    # Terribly sorry about this Mac users, I didn't bother handling Apple devices here.
    
    if PLATFORM.startswith('linux'):
        player.set_xwindow(window['videoStreamOutput'].Widget.winfo_id())
    else:
        player.set_hwnd(window['videoStreamOutput'].Widget.winfo_id())
    
    player.play()

    return window

def openPostVideoWatch(window):
    global player
    
    event,values = window.read(100)
    
    basename = window.metadata["videoBasename"]

    if(event==sg.WIN_CLOSED):
        window.close()
        player.stop()
        return (True,True) # break, no failure

    if (event == "openPostVideoClose_" + basename):
        window.close()
        from src.func.parentHandler import parentHandler
        if window.metadata["parent"]: parentHandler(window.metadata["parent"])
        return (True,True) # break, no failure
    
    if (event == "openPostVideoPlayPause_" + basename):
        player.pause()
    
    elif (event == "openPostVideoMute_" + basename):
        player.audio_toggle_mute()
    
    elif (event == "openPostVideoFrontArrow_" + basename):
        player.set_time(player.get_time() + 10000)
    
    elif (event == "openPostVideoBackArrow_" + basename):
        player.set_time(player.get_time() - 10000)
        

openPostVideo = externalFuncs.WinElement(openPostVideoWatch, window=openPostVideoWindow)