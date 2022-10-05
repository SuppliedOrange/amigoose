import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs
from src.func import layoutParser as lp

def topLayout(subreddit):
    defaultFont = externalFuncs.getDefaultFont()
    addIcon = externalFuncs.getButton("add")
    subredditIcon = imageFuncs.convertToB64( imageFuncs.convertToPFP( imageFuncs.getIcon(subreddit) ,(200,200), cacheOutput=(subreddit, "subreddit")) )
    sg.theme(externalFuncs.getTheme())
    buttonColor = ("white" if externalFuncs.isThemeDark() else "black", sg.theme_background_color())
    userDB = externalFuncs.initUserDB()

    topLayout = [
        [sg.Button(image_data=subredditIcon, image_subsample=3, button_color= buttonColor, border_width=0, key="subreddit+top_open_details-" + subreddit ),
         sg.Push(),
         sg.Button(image_filename=addIcon, image_subsample=9, button_color= buttonColor, border_width=0, key="subreddit+top_add_post-" + subreddit),
         sg.Button("new", font=(defaultFont,28), button_color=buttonColor, border_width=0, key="subreddit+top_open_new-" + subreddit),
         sg.Button("top", font=(defaultFont,28), button_color = ("gray", sg.theme_background_color()), border_width=0)
        ],
        [sg.HorizontalSeparator()],
        [sg.Column(
            [*lp.postCardHandler(
                *[x[2] for x in userDB["postData"].getPostsBy(subreddit=subreddit, orderby="honks")]
                )],
            scrollable=True, vertical_scroll_only=True, expand_x=True, expand_y=True, sbar_relief=sg.RELIEF_FLAT
        )]
    ]
    
    return topLayout

def topExec(event,values,window):

    if event and ("-" in event) and (event.split("-")[1] == window.metadata["subreddit"]):
        event = event.split("-")[0]

    if (event == "subreddit+top_open_details"):
        externalFuncs.moveTab(window, "subredditTabgroup", "topTab", "subredditTab")

    elif (event == "subreddit+top_open_new"):
        externalFuncs.moveTab(window, "subredditTabgroup", "topTab", "newTab")

top = externalFuncs.TabElement(exec=topExec, layout=topLayout)