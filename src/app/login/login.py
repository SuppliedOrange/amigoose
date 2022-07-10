import PySimpleGUI as sg
from src.func import externalFuncs, imageFuncs
from src.crypto import decrypt
from src.dbfunc import sqlfunc,fixData
from src.app.login.register import checkValid
sqlfunc.selectDB('global')
fixData.fixData()

showpass = externalFuncs.getPath("./assets/amigoose_assets/showpass.png")
hidepass = externalFuncs.getPath("./assets/amigoose_assets/hidepass.png")
is_elegant = (sqlfunc.getData("loginManager",(),"loginStyle")[0] == "Elegant")
loginDeselect = externalFuncs.getPath(f"./assets/amigoose_assets/login_{'inactive' if is_elegant else 'normal'}.png") #login_normal or login_inactive
loginSelect = externalFuncs.getPath(f"./assets/amigoose_assets/login_{'active' if is_elegant else 'glow'}.png") # login_glow or login_active
registerDeselect = externalFuncs.getPath(f"./assets/amigoose_assets/register_{'inactive' if is_elegant else 'normal'}.png") # register_normal or register_inactive
registerSelect = externalFuncs.getPath(f"./assets/amigoose_assets/register_{'active' if is_elegant else 'glow'}.png") # register_glow or register_active

defaultFont = sqlfunc.getData("loginManager",(),"defaultFont")[0]

def loginWindow():

    sqlfunc.updateData('loginManager','hidePasswordLogin',0,())
    sqlfunc.updateData('loginManager','hidePasswordRegister',0,())
    sg.theme('reddit')
    loginLayout = [
        [sg.Button(image_filename=loginSelect,border_width=0,button_color="white",image_subsample=4,image_size=(190,75)), sg.Button(image_filename=registerDeselect,border_width=0,button_color="white",image_subsample=4,image_size=(250,75),key='moveToRegisterTab')],
        [sg.Text("Username",font=(defaultFont,15))],
        [sg.Input(focus=True,background_color="white",border_width=0.5,key="user_login")],
        [sg.Text("Password",font=(defaultFont,15)),sg.Button(image_filename=hidepass,key='viewPass_login',image_size=(25,25), image_subsample=6, button_color="white")],
        [sg.Input(password_char="*",background_color="white",border_width=0.5,key='pass_login')],
        [sg.T('',text_color="red",key='err_login',font=(defaultFont,20))],
        [sg.Button("Submit", key="submit_login")]
    ]

    registerLayout = [
        [sg.Button(image_filename=loginDeselect,border_width=0,button_color="white",image_subsample=4,image_size=(190,75),key='moveToLoginTab'), sg.Button(image_filename=registerSelect,border_width=0,button_color="white",image_subsample=4,image_size=(250,75))],
        [sg.Text("Username",font=(defaultFont,15))],
        [sg.Input(focus=True,background_color="white",border_width=0.5,key="user_register")],
        [sg.Text("Password",font=(defaultFont,15)),sg.Button(image_filename=hidepass,key='viewPass_register',image_size=(25,25), image_subsample=6, button_color="white")],
        [sg.Input(password_char="*",background_color="white",border_width=0.5,key='pass_register1')],
        [sg.Text("Repeat Password",font=(defaultFont,15))],
        [sg.Input(password_char="*",background_color="white",border_width=0.5,key='pass_register2')],
        [sg.T('',text_color="red",key='err_register',font=(defaultFont,20))],
        [sg.Button("Create", key="create_login")]
    ]

    tabs = [
            sg.Tab("Login",loginLayout,key='loginTab'),
            sg.Tab("Register",registerLayout,key='registerTab',visible=False)
        ]
    layout = [[sg.TabGroup([tabs], key='tabgroup', expand_x=True, expand_y=True)]]
    window = sg.Window("Amigoose",layout.copy(),size=(450,425),resizable=True, icon=imageFuncs.getLogo(), metadata={
        "tabs": list(map(lambda x: x.Key ,tabs))
    })
    window.finalize()
    bindKeys(window, "user_login","pass_login","user_register","pass_register1","pass_register2")
    return window

def loginWatch(window):
    event,values = window.read(100)

    try:
        username = values['user_login'] or values['user_register']
    except:
        return (True,False) # break, failure

    if(event==sg.WIN_CLOSED):
        window.close()
        return (True,False) # break, failure
    
    elif (event == "__TIMEOUT__"): pass

    elif(event == "submit_login"):
        validate = decrypt(username,values['pass_login'])
        if validate[0]:
            window.close()
            print("Successfully logged into",username)
            sqlfunc.selectDB('global')
            sqlfunc.updateData("loginState","username",username,())
            return (True,username) # break, success (true)
        else:
            window['err_login'].update(validate[1])

    elif (event == 'viewPass_login'):
        sqlfunc.selectDB('global')
        showPassword = sqlfunc.getData("loginManager",(),"hidePasswordLogin")[0]
        if not showPassword:
            window['viewPass_login'].update(image_filename=showpass,image_subsample=6,image_size=(25,25))
            window['pass_login'].update(password_char='')
            sqlfunc.updateData('loginManager','hidePasswordLogin',1,())

        else:
            window['viewPass_login'].update(image_filename=hidepass,image_subsample=6,image_size=(25,25))
            window['pass_login'].update(password_char='*')
            sqlfunc.updateData('loginManager','hidePasswordLogin',0,())

    elif (event == 'viewPass_register'):
        sqlfunc.selectDB('global')
        showPassword = sqlfunc.getData("loginManager",(),"hidePasswordRegister")[0]
        if not showPassword:
            window['viewPass_register'].update(image_filename=showpass,image_subsample=6,image_size=(25,25))
            window['pass_register1'].update(password_char='')
            window['pass_register2'].update(password_char='')
            sqlfunc.updateData('loginManager','hidePasswordRegister',1,())

        else:
            sqlfunc.selectDB('global')
            window['viewPass_register'].update(image_filename=hidepass,image_subsample=6,image_size=(25,25))
            window['pass_register1'].update(password_char='*')
            window['pass_register2'].update(password_char='*')
            sqlfunc.updateData('loginManager','hidePasswordRegister',0,())
    
    elif (event == 'moveToLoginTab'):
        externalFuncs.moveTab(window,"tabgroup","registerTab","loginTab")
        clearValues(window, "user_register", "pass_register1","pass_register2")
    elif (event == 'moveToRegisterTab'):
        externalFuncs.moveTab(window,"tabgroup","loginTab","registerTab")
        clearValues(window, "user_login","pass_login")
        window['create_login'].update(disabled=False)

    elif (event == 'create_login'):
        valid = checkValid(window,values)
        window['err_register'].update(valid[1])

    elif ("-" in event):
        value,type = event.split("-")
        
        if type == "pressed_enter":
            # When enter is clicked while having selected any input element, activate the next element in corrospondence
            if value == "user_login": window["pass_login"].SetFocus()
            elif value == "pass_login": window["submit_login"].Click()
            elif value == "user_register": window["pass_register1"].SetFocus()
            elif value == "pass_register1": window["pass_register2"].SetFocus()
            elif value == "pass_register2": window["create_login"].Click() 

def bindKeys(window, *keys):
    """ Each time Enter key is clicked while having selected any of these elements, an event will be distributed. """
    for key in keys:
        window[key].bind("<Return>","-pressed_enter")
        window[key].bind("<Tab>", "-pressed_enter")

def clearValues(window,*keys):
    """ Update the element to have no text in it """
    for key in keys:
        window[key].update('')


login = externalFuncs.WinElement(loginWatch,window=loginWindow)