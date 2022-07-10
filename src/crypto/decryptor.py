def decrypt(username,password):
    from .cipher_suite import getEncryptionKey
    from dbfunc.sqlfunc import loadColumn,getData,selectDB
    selectDB("accounts")

    if (not username in loadColumn("tokens","username")):
         return (False,"Invalid Username")
    try:
        cipher_suite = getEncryptionKey(username)
    except Exception as e:
        return (False, "Error: Invalid encryption key\n",e)
        
    passwords = loadColumn("passwords","username")

    if (not username in passwords):
        return (False, "Error: Username not in password database")
    
    encrypted_password = getData("passwords", ("username",username), "password")[0]
    
    decoded_text = cipher_suite.decrypt(bytes(encrypted_password,'utf-8'))
    if (str(decoded_text,'utf-8') != password):
        return (False, "Incorrect Password")
    
    return (True, "Access Granted")
    