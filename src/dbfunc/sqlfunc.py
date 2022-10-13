import mysql.connector
from .formats import formats
from . import dataTables

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="dpsbn"
)

if (not db.is_connected()):
    print("ERROR CONNECTING TO DATABASE")

cursor = db.cursor()


def readAll():
    try:
        # important to read all the cursor data before attaching more data to the cursor
        return cursor.fetchall()
    except:
        pass


def selectDB(db):
    """
    DB - The DB to select - String
    """
    readAll()
    return cursor.execute("USE " + db)


def cleanConnection():
    """
    To close the database connection
    """
    db.close()


def loadColumn(table, column):
    """
    Table - A table in the selected database - String\n
    Column - A column in the table - String\n
    """
    readAll()
    query = "SELECT " + column + " FROM " + table
    cursor.execute(query)
    result = cursor.fetchall()
    result = list(map(lambda x: x[0], result))
    return result


def insertData(table, values):
    """
    Table - A table in the selected database - String\n
    Values - Values for inserting into table. All column values must be provided - Tuple( String, Int, Bool..)\n
    """
    readAll()
    syntax = None
    try:
        syntax = getFormat(table).columns
    except Exception as e:
        print(e)
        return (False, "Invalid table")

    placeHolder = "(" + ("%s," * (len(values) - 1)) + "%s)"
    query = "INSERT INTO " + table + ' ' + syntax + ' VALUES ' + placeHolder
    cursor.execute(query, values)
    db.commit()
    print(cursor.rowcount, "records affected")


def getFormat(table):
    """
    Table - A table in the selected database - String\n
    """
    currdb = executeSQL("SELECT DATABASE() FROM DUAL").fetchone()[0]
    tables = None
    try:
        tables = formats[currdb].keys()
    except Exception as e:
        print(e or repr(e))
        raise Exception
    if not table in tables:
        return False
    return formats[currdb][table]


def deleteData(table, *operators):
    """ 
    Table - A table in the selected database - String\n
    Operators - Identifiers - Tuple( String, String ), Tuple( String, String )...\n
    """
    readAll()
    # Operators = ( (column, key), (column, key), ...)
    identifier = operators[0]
    keys = loadColumn(table, identifier[0])
    if not identifier[1] in keys:
        print("key does not exist in this database.")
        return (False, "Key Non-Existent")
    query = "DELETE FROM " + table + " WHERE "
    for key in enumerate(operators):
        index, operator = key
        query = query + (" AND " if index != 0 else "") + \
            operator[0] + " = " + "\"{}\"".format(operator[1])
    cursor.execute(query)
    db.commit()
    print(cursor.rowcount, "records affected")


def executeSQL(query, commit=False):
    """
    Query - Your SQL query - String\n
    Commit - Whether to commit after executing the cursor - Boolean\n
    Returns a cursor\n
    """
    readAll()
    cursor.execute(query)
    if (commit):
        db.commit()
    return cursor


def updateData(table, toUpdateColumn, toUpdateValue, identifier):
    """
    Table - A table in the selected database - String\n
    toUpdateColumn - The column in which the update takes place - String\n
    toUpdateValue - The value to update to - String/Integer\n
    Identifier - Identifier to locate correct row (Column, Value) - Tuple( String, String )\n
    """
    readAll()
    # identifier = (identifier (0), identifierValue (1))
    query = "UPDATE " + table + " SET " + toUpdateColumn + " = %s"
    values = (toUpdateValue,)
    if identifier:
        keys = loadColumn(table, identifier[0])
        if not identifier[1] in keys:
            print(
                "identifier key does not exist in this database\nidentifier key provided:", identifier[1])
            return
        query = query + " WHERE " + identifier[0] + " = %s"
        values = values + (identifier[1],)
    cursor.execute(query, values)
    db.commit()
    print(cursor.rowcount, "records affected")


def getData(table, identifier, columnToGet, fetchAll=False):
    """
    Table - A table in the selected database - String\n
    Identifier - Identifier to locate correct row(s) in the form of (Column, Value) - Tuple( String, String )\n
    columnToGet - The column to get entries from - String\n
    fetchAll - Whether to fetch all entries in the form of a list - Boolean\n

    """
    readAll()
    query = "SELECT " + columnToGet + " FROM " + table
    if identifier:
        query = query + " WHERE " + \
            identifier[0] + " = " + "'{}'".format(identifier[1])
    cursor.execute(query)
    result = cursor.fetchall() if fetchAll else cursor.fetchone()
    if type(result) == list and fetchAll:
        result = tuple(map(lambda x: x[0], result))
    return result


def searchData(table, column, searchFor, fetchAll=False):
    """
    Table - A table in the selected database - String\n
    Column - The column to search in - String\n
    searchFor - The value to search for - String\n
    fetchAll - Whether to fetch all entries in the form of a list - Boolean\n
    """
    readAll()
    query = "SELECT " + column + " FROM " + table + \
        " WHERE " + column + ' LIKE "%' + searchFor + '%"'
    cursor.execute(query)
    result = cursor.fetchall() if fetchAll else cursor.fetchone()
    if type(result) == list and fetchAll:
        result = tuple(map(lambda x: x[0], result))
    return result


def deleteAccount(username):
    """
    Username - The username of the user to be deleted from all entries - String\n
    """
    userDB = dataTables.dataTables(username).initializeUser()
    userDB["userData"].deleteAccount()
    return (True, "Success")


def dropAll():
    """
    Drops every database in formats\n
    Clears all subreddit tags\n
    Don't use this, I don't even know if I did this right.
    """

    import os
    from pathlib import Path

    # Dropping all tables
    for database in formats:
        try:
            executeSQL("DROP DATABASE " + database)
            print("dropped db", database)
        except: pass
    print(cursor.rowcount, "records affected")

    # Clearing all tags
    from .jsonfunc import updateFile
    updateFile({})
    print("Cleared tags.json")

    # Remove the CSV file too!

    def clearFolder(path):
        [f.unlink() for f in Path(path).glob("*.png") if f.is_file()]

    # Removing all user profile pictures
    clearFolder(os.path.abspath("./assets/user_assets/pfps/"))
    # Removing all subreddit icons
    clearFolder(os.path.abspath("./subreddits/pfps/"))
    # Removing all cached subreddit pfps
    clearFolder(os.path.abspath(
        "./assets/remote_assets/cache/subreddit_pfps/"))
    # Removing all cached user pfps
    clearFolder(os.path.abspath("./assets/remote_assets/cache/user_pfps/"))


def existingUser():
    """
    Returns currently logged in user or None
    """
    readAll()
    selectDB("global")
    return getData("loginState", (), "username")[0] or None


def checkMatch(table, *checkers):
    """
    Check if one or more criteria is met in a column\n
    Table - A table in the selected database - String\n
    Checkers - *(Column, Value) - *Tuples\n
    """
    readAll()
    query = "SELECT * FROM " + table + " WHERE "
    for ind, val in enumerate(checkers):
        query = query + val[0] + " = '" + val[1] + \
            ("' AND " if ind != len(checkers) - 1 else "'")
    cursor.execute(query)
    return bool(cursor.fetchone())