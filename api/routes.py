# flask packages
from flask_restful import Api

# project resources
from api.productionplan import ProductionPlanApi


def create_routes(api: Api):
    """Adds resources to the api.
    :param api: Flask-RESTful Api Object
    :Example:
        api.add_resource(HelloWorld, '/', '/hello')
        api.add_resource(Foo, '/foo', endpoint="foo")
        api.add_resource(FooSpecial, '/special/foo', endpoint="foo")
    """
    api.add_resource(ProductionPlanApi, '/productionplan')

