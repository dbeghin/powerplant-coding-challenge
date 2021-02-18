# flask packages
from flask import Response, request, jsonify
from flask_restful import Resource

# project resources
from models.powerplant import PowerPlant
from api.errors import forbidden
from functions.optimisation import optimise

#external packages
import logging
logging.basicConfig(filename='error_and_info.log', filemode='w', format='%(levelname)s: %(message)s', level=logging.INFO)


default_solution = [
    {
        "name": "windpark1",
        "p": 75
    },
    {
        "name": "windpark2",
        "p": 18
    },
    {
        "name": "gasfiredbig1",
        "p": 200
    },
    {
        "name": "gasfiredbig1",
        "p": 0
    },
    {
        "name": "tj1",
        "p": 0
    },
    {
        "name": "tj2",
        "p": 0
    }
]



class ProductionPlanApi(Resource):
    """
    Flask-resftul resource for returning db.user collection.
    :Example:
    >>> from flask import Flask
    >>> from flask_restful import Api
    >>> from app import default_config
    # Create flask app, config, and resftul api, then add UserApi route
    >>> app = Flask(__name__)
    >>> app.config.update(default_config)
    >>> api = Api(app=app)
    >>> api.add_resource(UserApi, '/user/<user_id>')
    """
    def get(self) -> Response:
        """
        GET response for debugging
        :return: JSON object
        """
        solution = default_solution
        
        return jsonify({'result': solution})

    
    #def put(self, user_id: str) -> Response:
    #    """
    #    PUT response method for updating a user.
    #    JSON Web Token is required.
    #    Authorization is required: Access(admin=true) or UserId = get_jwt_identity()
    #    :return: JSON object
    #    """
    #    data = request.get_json()
    #    put_user = Users.objects(id=user_id).update(**data)
    #    output = {'id': str(put_user.id)}
    #    return jsonify({'result': output})
    
    
    def post(self) -> Response:
        """
        POST response method for optimising load.
        :return: JSON object
        """
        logging.info("New POST request.")
        data = request.get_json(silent=True)
        if data == None:
            error_message = "Unable to parse JSON. Check content of JSON file and/or the CURL command used."
            logging.error(error_message)
            return jsonify({'error': error_message})

        output = optimise(data)
        return jsonify({'result': output})

    
    #def delete(self, user_id: str) -> Response:
    #    """
    #    DELETE response method for deleting user.
    #    JSON Web Token is required.
    #    Authorization is required: Access(admin=true)
    #    :return: JSON object
    #    """
    #    authorized: bool = Users.objects.get(id=get_jwt_identity()).access.admin
    #
    #    if authorized:
    #        output = Users.objects(id=user_id).delete()
    #        return jsonify({'result': output})
    #    else:
    #        return forbidden()
