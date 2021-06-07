import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
import initdb as cn

class User(UserMixin):
    def __init__(self,userid=None,login=None,password=None,status=None, email=None, phone=None):
        self.userid = userid
        self.login = login
        self.password = password
        self.status = status
        self.email = email
        self.phone = phone

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return self.userid

@login.user_loader
def load_user(userid):
    conn = cn.get_connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM person WHERE userid = %s;"
    cursor.execute(sql, (int(userid),))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result is None:
        user = None
    else:
        user = User(result['userid'], result['login'], result['password'], result['status'], result['email'], result['phone'])
    return user 


  