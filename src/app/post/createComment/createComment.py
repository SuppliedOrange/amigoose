import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs
from random import choice

def createCommentWindow(uuid, author):
    userDB = externalFuncs.initUserDB()
    defaultFont = userDB["settings"].getPreference("font")
    prompt = choice(["Write a honkin' good comment", "One honkin' good comment coming up!", "Geese-friendly, please!", "Write down your goose thoughts"])

    sg.theme(externalFuncs.getTheme())
    
    changeUsernameLayout = [
        [sg.Text(prompt, font=(defaultFont,15))],
        [sg.Multiline("...", size=(100,20), k="createComment_textbox")],
        [sg.Text(text_color="red", k="createComment_toast")],
        [sg.Button("Comment", disabled=True, k="createComment_confirm")]
    ]

    window = sg.Window("Amigoose - Making a comment", layout = changeUsernameLayout.copy(), resizable=True, element_justification="c", margins=(0,0), element_padding=(0,0), finalize=True, auto_size_text=True, keep_on_top=True, modal=True, icon=imageFuncs.getLogo(), alpha_channel=externalFuncs.getWindowOpacity(), metadata={
        "uuid": uuid,
        "author": author
    })
    window.make_modal()
    return window

def createCommentWatch(window):

    event,values = window.read(100)
    event = externalFuncs.sanitizeEvent(event)

    method,value = event.split("-") if event and "-" in event else (None,None)

    if(event==sg.WIN_CLOSED):
        window.close()
        return (True,True) # break, no failure
    
    comment_length = len(values['createComment_textbox'])
    comment_invalid = comment_length > 1000 or comment_length < 1
    window["createComment_toast"].update(f"{comment_length}/1000", text_color="red" if comment_invalid else "blue")
    window["createComment_confirm"].update(disabled = comment_invalid)

createComment = externalFuncs.WinElement(createCommentWatch, window=createCommentWindow)