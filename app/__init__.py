from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
USERS = []  # This is a list of User objects
POSTS = []  # This is a list of Post objects

from app import views
from app import models
