from flask import Flask
from flask_bootstrap import Bootstrap
from config import Config
from flask_login import LoginManager


app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = 'login'
Bootstrap(app)


from app import routes
