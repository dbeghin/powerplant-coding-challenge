# flask packages
from flask import Flask, app
from flask_restful import Api

# local packages
from api.routes import create_routes

# external packages
import os

# default configuration
#default_config = {'MONGODB_SETTINGS': {
#                    'db': 'test_db',
#                    'host': 'localhost',
#                    'port': 27017,
#                    'username': 'admin',
#                    'password': 'JigsawFalling',
#                    'authentication_source': 'admin'},
#                  'JWT_SECRET_KEY': 'changeThisKeyFirst'}


def get_flask_app(config: dict = None) -> app.Flask:
    """
    Initializes Flask app with given configuration.
    Main entry point for wsgi (gunicorn) server.
    :param config: Configuration dictionary
    :return: app
    """
    # init flask
    flask_app = Flask(__name__)

    # configure app
    #config = default_config if config is None else config
    #flask_app.config.update(config)
    
    # load config variables
    #if 'MONGODB_URI' in os.environ:
    #    flask_app.config['MONGODB_SETTINGS'] = {'host': os.environ['MONGODB_URI'],
    #                                            'retryWrites': False}

    # init api and routes
    api = Api(app=flask_app)
    create_routes(api=api)

    return flask_app


if __name__ == '__main__':
    # Main entry point when run in stand-alone mode.
    app = get_flask_app()
    app.run(host="127.0.0.1", port=8888, debug=True)
