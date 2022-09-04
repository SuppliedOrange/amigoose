import mysql.connector as tor

def initialize():
    conn = tor.connect(host="localhost", user = "root", password="dpsbn")
    if not conn.is_connected():
        raise Exception
    return conn

connection = initialize()
cursor = connection.cursor()

def addRecords(*values):
    """
    Arguments for addRecords:
    => iterable(pid,productname,manufacturer,price), iterable(pid,productname,manufacturer,price)... and so on
    => Example: ("XQC1", "Vinegar", "HAR", 1234), ("YOLO", "Wooden Plank", "POP", 1030)
    """
    query = "insert into product values "
    #query += "('" + "','".join(item) + "')"
    for value in values:
        value = str(value)
        query += value + ","

    # Remove the last , from the string.
    query = query[:-1]

    # Instead of using None, since we're using complete strings, we use "NULL". Don't use None.
    query = "NULL".join(query.split("None"))

    cursor.execute(query)
    connection.commit()
    return cursor.rowcount

def showRecords(x=None):
    """
    Returns all records. Press enter to continue
    """
    query = "select * from product"
    cursor.execute(query)
    return cursor.fetchall()

def showRecordsByManufacturer(mnf):
    """
    Arguments for showRecordsByManufacturer:
    => string(manufacturer)
    """    
    query = "select * from product where manufacturer ='{manufacturer}'".format(manufacturer=mnf)
    cursor.execute(query)
    return cursor.fetchall()

def modify_p_id(args):
    """
    Arguments for modify_p_id
    => string(p_id), string(price)
    Must be separated by a comma.
    """
    args = args.split(",")
    p_id, price = args
    query = "update product set price = '%s' where p_id = '%s'"%(price, p_id)
    cursor.execute(query)
    connection.commit()
    return cursor.rowcount

def deleteRecord(product_name):
    """
    Arguments for deleteRecord:
    => string(product_name)
    """    
    query = f"delete from product where productname = '{product_name}'"
    cursor.execute(query)
    connection.commit()
    return cursor.rowcount

def killConnection(x=None):
    """
    Kills the connection. Press enter to kill.
    """    
    return connection.close()

greeting = "Welcome to question 1 of MySQL Connectivity that Varsha ma'am asked me to do\nYou may modify the table by entering any of the following numbers followed by arguments. Use help to know more\n"

guide = "1: add records\n2: show all records\n3: show records by manufacturer\n4: modify product id\n5: delete a record\n6: kill the connection and exit\n"

def commandHandler(cmd):

    if (cmd.lower() == "help"):
        return(False, guide)

    try:
        cmd = int(cmd)
    except:
        return (False, "Hey, that's not an integer! Use integers between 1 to 6 or use help\n")
        

    cmdlist = {
        1: addRecords,
        2: showRecords,
        3: showRecordsByManufacturer,
        4: modify_p_id,
        5: deleteRecord,
        6: killConnection
        }

    if cmd not in cmdlist:
        return (False, "Hey, that's not a valid command. Use help for more info\n")

    cursor.fetchall() # -> to prevent unread cursors.

    return (True, cmdlist[cmd])

def fixData():
    print("Attempting to fix some missing data.")
    cursor.execute("create database if not exists shop")
    cursor.fetchall()
    cursor.execute("use shop")
    cursor.fetchall()
    cursor.execute(" create table if not exists product ( p_id char(4), productname varchar(100), manufacturer char(3), price int ); ")
    cursor.fetchall()
    addRecords(
        ("TP01", "Talcum Powder", "LAK", 40),
        ("FW05", "Face Wash", "ABC", 45),
        ("BS01", "Bath Soap", "ABC", 55),
        ("SH06", "Shampoo", "XYZ", 120),
        ("FW12", "Face Wash", "XYZ", None)
    )
    print("Done!\nCurrent Table:")
    cursor.execute("select * from product")
    print(cursor.fetchall())

try:
    cursor.execute("use shop")
except:
    fixData()

print(greeting)
print(guide)

while True:
    cmd = commandHandler(input("Enter a function number\n-> "))

    if not cmd[0]:
        print(cmd[1])
        continue

    print(cmd[1].__doc__)

    arg = input("")

    try:
        print(cmd[1](arg))
    except Exception as e:
        print("Something went wrong! Here's the full error.\n")
        print("Provided arguments:", arg)
        print(e)

    if cmd[1] == killConnection:
        print("Connection broken! Goodbye!\n")
        break