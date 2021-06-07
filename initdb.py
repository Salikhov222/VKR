import psycopg2
from transliterate import translit, get_available_language_codes
from psycopg2 import sql
from psycopg2.extras import DictCursor
from werkzeug.security import generate_password_hash, check_password_hash
import os
import urllib.parse as urlparse

""" url = urlparse.urlparse(os.environ['DATABASE_URL'])
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port """

con = psycopg2.connect(
                            dbname="hunterhead",
                            user="salikhov",
                            password="123456",
                            host="127.0.0.1",
                            port="5432",
                            )
cur = con.cursor()

def get_connection():
    conn = psycopg2.connect(
                            dbname="hunterhead",
                            user="salikhov",
                            password="123456",
                            host="127.0.0.1",
                            port="5432",
                            cursor_factory=DictCursor
                            )
    return conn 

def get_connection2():
    conn = psycopg2.connect(
                            dbname="hunterhead",
                            user="salikhov",
                            password="123456",
                            host="127.0.0.1",
                            port="5432",
                            )
    return conn     

def createAdmin():
    adminPswdHash = generate_password_hash('admin')
    try:
        cur.execute("INSERT INTO person (login, password, status, email, phone) VALUES ('admin', %s, 'admin', 'admin@admin.ru', '0000000000')", (adminPswdHash,))
        con.commit()
    except psycopg2.Error:
        con.rollback()
        pass


def loadInfoFromProfile(columnname, tablename, name):
    cur.execute(
        sql.SQL("SELECT {0} FROM {1} WHERE userid = (select userid from person where login = %s)")
            .format(sql.Identifier(columnname), sql.Identifier(tablename)),[name])
    result = cur.fetchone()
    profileData = ''
    if result is not None:
        profileData = result[0]
    con.commit()
    return profileData

def loadInfoFromPerson(columnname, name):
    cur.execute(
        sql.SQL("SELECT {} FROM person WHERE userid = (select userid from person where login = %s)")
            .format(sql.Identifier(columnname)), [name])
    result = cur.fetchone()
    profileData = ''
    if result is not None:
        profileData = result[0]
    con.commit()
    return profileData

def userExist(tablename, id):
    cur.execute(sql.SQL("SELECT userid FROM {} WHERE userid = %s").format(sql.Identifier(tablename)), [id])
    result = cur.fetchone()
    if result is not None:
        item = 1
    else:
        item = 0
    con.commit()
    return item

def selectColumn(columnname, tablename):
    cur.execute(sql.SQL("SELECT {0} FROM {1}").format(sql.Identifier(columnname), sql.Identifier(tablename)))
    result = cur.fetchall()
    result_new = list(sum(result, ()))
    con.commit()
    return result_new

def getUserID(name):
    cur.execute('SELECT userid FROM person WHERE login = %s', (name,))
    result = cur.fetchone()
    ID = ''
    if result is not None:
        ID = result[0]
    con.commit()
    return ID

def translitToURL(data):
    dataUni = translit(data, 'ru', reversed=True)
    dataURL = "_".join(dataUni.split())
    return dataURL

def translitFromURL(data):
    dataURL = translit(data, 'ru')
    dataURL = dataURL.lower()
    dataRus = dataURL.replace('_', ' ')
    return dataRus

