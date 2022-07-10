def getEncryptionKey(username):
    from cryptography.fernet import Fernet
    from dbfunc.sqlfunc import getData,insertData,loadColumn,selectDB
    selectDB("accounts")
    
    tokensUsernames = loadColumn("tokens","username")

    if (not username in tokensUsernames):
        key = str(Fernet.generate_key(),'utf-8')
        print("Performing first-time user encryption")
        insertData("tokens",(username,key))

    token = getData("tokens",("username",username),'token')[0]

    encryption_key = token

    try:
        return Fernet(encryption_key)
    except Exception as e:
        print("Error while reading encryption key.\n",e)
        return (None)