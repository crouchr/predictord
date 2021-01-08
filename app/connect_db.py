import mysql.connector

def connect_database(mysql_host, db_name):
    """

    :return:
    """
    mydb = mysql.connector.connect(
        host=mysql_host,
        database=db_name,
        user="metmini",
        password="metmini"
    )

    mycursor = mydb.cursor()

    return (mydb, mycursor)
