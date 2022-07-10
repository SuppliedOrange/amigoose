def encrypt(username,password):
    from .cipher_suite import getEncryptionKey
    from dbfunc.sqlfunc import insertData,updateData,loadColumn,selectDB,getData
    selectDB("accounts")

    vUsername = usernameValidator(username)
    if not vUsername[0]: return vUsername
    
    try:
        cipher_suite = getEncryptionKey(username)
    except Exception as e:
        print("Error while getting encryption key\n",e)
        return (False, "Error while getting encryption key")
    try:
        encoded_password = cipher_suite.encrypt(bytes(password,'utf-8'))
        encoded_password = str(encoded_password,'utf-8')
    except Exception as e:
        print("Error while encrypting password\n",e)
        return (False, "Error while encrypting password")
    
    # Uploading password to passwords.json (now in sql because why not)
    passwordsUsernames = loadColumn("passwords","username")
    
    if not username in passwordsUsernames:
        from time import time
        from func.externalFuncs import getFonts
        # set username to encoded password
        insertData("passwords",(username,encoded_password))
        selectDB("settings")
        font = "Bahnschrift" if "Bahnschrift" in getFonts() else "Calibri"
        insertData("preferences",(username, "reddit", font, 1.0)) # you'll need to add all default preferences before an account creation
        selectDB("userData")
        insertData("profileData",(username, 0, int(time()), ""))
    else:
        updateData("passwords","password",encoded_password,("username",username))

    return (True,'success')

def usernameValidator(username):
    from dbfunc.sqlfunc import getData,selectDB

    if len(username) < 1 or len(username) > 15:
        return (False, "Username length must be 1-15 characters")

    if " " in username:
        return (False, "Username cannot contain spaces")
    
    selectDB("accounts")
    if getData('tokens',('username',username),'username',fetchAll=True):
        return (False, "Username taken")
    
    validChars = list("1234567890qwertyuiopasdfghjklzzxcvbnm/._")
    if not all(letter.lower() in validChars for letter in username):
        return (False, "Your username can only alphanumeric and . @ _ characters.")

    return (True,)