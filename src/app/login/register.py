from src.crypto import encrypt
from src.dbfunc import sqlfunc

def checkValid(window,values):
    sqlfunc.selectDB('accounts')
    username = values['user_register']
    if not all([values['pass_register1'],values['pass_register2'],username]):
         return (False, "Fields cannot be empty")
    if not values['pass_register1'] == values['pass_register2']:
        return (False,"Passwords do not match")
    tryEncrypting = encrypt(username,values['pass_register1'])
    if not tryEncrypting[0]:
        return (False,tryEncrypting[1])
    sqlfunc.selectDB('global')
    window['create_login'].update(disabled=True)
    return (True,"Account Created!")