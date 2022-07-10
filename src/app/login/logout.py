from src.dbfunc import sqlfunc

def logout():
    sqlfunc.selectDB('global')
    sqlfunc.updateData("loginState","username",None,())