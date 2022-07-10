from src.dbfunc import sqlfunc,fixData
#sqlfunc.dropAll()
fixData.fixData()

 # Check if there is a currently logged in user
username = sqlfunc.existingUser()

if not username:
    from src.app.login.login import login
    username = login.start() # Get the user to login otherwise

print("Current Account:",username)

from src.app.home.home import home
home.start()