from flask import Flask

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('server.settings.DevelopmentConfig')


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return


# Register blueprints
def register_blueprints(app):
    # Prevents circular imports
    # Import a module / component using its blueprint handler variable (mod_auth)
    from server.configuration.controllers import config
    from server.control.controllers import control
    from server.monitor.controllers import monitor

    # Register blueprint(s)
    app.register_blueprint(config)
    app.register_blueprint(control)
    app.register_blueprint(monitor)


register_blueprints(app)
