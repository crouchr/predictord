# fixme : note host is localhost
import mysql.connector

# host="erminserver.localdomain",
def connect_database(db_name):
    """

    :return:
    """
    mydb = mysql.connector.connect(
        host="192.168.1.15",
        database=db_name,
        user="metmini",
        password="metmini"
    )

    mycursor = mydb.cursor()

    return (mydb, mycursor)
