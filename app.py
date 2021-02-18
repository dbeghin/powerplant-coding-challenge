# flask packages
from flask import Flask, app
from flask_restful import Api

# local packages
from api.routes import create_routes

# external packages
import os



def get_flask_app(config: dict = None) -> app.Flask:
    """
    Initialises Flask app with given configuration.
    However no configuration is necessary to run this app.
    :param config: Configuration dictionary
    :return: app
    """
    # init flask
    flask_app = Flask(__name__)

    # init api and routes
    api = Api(app=flask_app)
    create_routes(api=api)

    return flask_app


if __name__ == '__main__':
    # Main entry point when run in stand-alone mode.
    #runnint on port 8888
    app = get_flask_app()
    app.run(host="127.0.0.1", port=8888, debug=True)
