import mysql.connector
from  config import DB2_CONFIG,DB1_CONFIG
# def connection(app):
#     conn = mysql.connector.connect(
#          user = config.dbuser,
#          password = config.dbpassword,
#          database = config.dbname)
#          #dbhost = config.dbhost)
#     cursor = conn.cursor()
#     return conn,cursor
# import mysql.connector

def get_connection(db_config):
    connection = mysql.connector.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"]
    )
    return connection

def close_connection(connection):
    if connection:
        connection.close()
def insertIntoDB(app,values):
    connection = get_connection(DB1_CONFIG)
    cursor = connection.cursor()
    query = f"INSERT INTO user (first_name,last_name,email_address,password,registered_on,created_by,created_date) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(query,values)
    connection.commit()
def selectFromDB(app,email_address):
    connection = get_connection(DB1_CONFIG)
    cursor = connection.cursor()
    query = f'SELECT * FROM user WHERE email_address=%s'
    cursor.execute(query,(email_address,))
    user = cursor.fetchone()
    return user
def store_feedback(tender_summary, feedback, likes,created_date):

    connection = get_connection(DB2_CONFIG)
    cursor = connection.cursor()
    sql = "INSERT INTO feedback (tender_summary, feedback, likes,time_stamp) VALUES (%s, %s, %s,%s)"
    values = (tender_summary, feedback, likes, created_date)

    try:
        cursor.execute(sql, values)
        connection.commit()
        print("Feedback stored successfully!")
    except mysql.connector.Error as err:
        print(f"Error storing feedback: {err}")
    


    



