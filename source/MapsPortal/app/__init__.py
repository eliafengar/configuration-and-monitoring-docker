# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

from flask_json import FlaskJSON

from flask import Flask, render_template

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config.DevelopmentConfig')

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

#initialize JSON Extension
json = FlaskJSON(app)

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Import a module / component using its blueprint handler variable (mod_auth)
from app.auth.controllers import auth as auth_module
from app.portal.controllers import portal as portal_module

# Register blueprint(s)
app.register_blueprint(auth_module)
app.register_blueprint(portal_module)

# Build the database:
# This will create the database file using SQLAlchemy
db.create_all()

from app.portal.models import Product, Project, Map
