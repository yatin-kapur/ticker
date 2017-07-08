from flask import Flask

app = Flask(__name__)

from ticker import views
