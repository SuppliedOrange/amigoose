from email.mime import image
import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs

def openPostImageWindow(imagePath, parent=None):
    maxwidth, maxheight = [int(x/1.05) for x in sg.Window.get_screen_size()]
    imagewidth, imageheight = imageFuncs.getImageDimensions(imagePath)
    [imagewidth,imageheight] = [imagewidth + int(imagewidth/2), imageheight + int(imageheight/2)]

    imageBasename = externalFuncs.getBasename(imagePath)
    back_button = externalFuncs.getButton("back_button")
    buttonColor = externalFuncs.getThemeBackground()
    userDB = externalFuncs.initUserDB()

    sg.theme(externalFuncs.getTheme())

    openPostImageLayout = [
        [sg.Button(image_filename=back_button, image_subsample=12, button_color= buttonColor, border_width=0, key="openPostImageClose_" + imageBasename)],
        [sg.T()],
        [sg.Image(filename=imagePath)]
    ]

    openPostImageLayout = [
        [sg.Column(
            openPostImageLayout, scrollable=(imagewidth > maxwidth or imageheight > maxheight), sbar_relief=sg.RELIEF_FLAT, sbar_background_color=externalFuncs.getThemeBackground(), size=(imagewidth,imageheight)
        )]
    ]

    window = sg.Window(externalFuncs.getBasename(imagePath), openPostImageLayout.copy(), size=(imagewidth,imageheight), resizable=True, alpha_channel=userDB["settings"].getPreference("opacity"),icon=imageFuncs.getLogo(), metadata={
        "parent": parent,
        "imageBasename": imageBasename
    })

    window.finalize()
    return window

def openPostImageWatch(window):
    
    event,values = window.read(100)
    event = externalFuncs.sanitizeEvent(event)

    if(event==sg.WIN_CLOSED):
        window.close()
        return (True,True) # break, no failure

    if (event == "openPostImageClose_" + window.metadata["imageBasename"]):
        window.close()
        from src.func.parentHandler import parentHandler
        if window.metadata["parent"]: parentHandler(window.metadata["parent"])
        return (True,True) # break, no failure

openPostImage = externalFuncs.WinElement(openPostImageWatch, window=openPostImageWindow)