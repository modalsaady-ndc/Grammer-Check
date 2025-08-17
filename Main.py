from flask import Flask, make_response, jsonify
from flask_restx import Api
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager
# from Operations.LogEvent import Log_ns
from Operation.interface import interface_ns



from exts import db
import psycopg2
import datetime




def create_app(config):
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    # CORS(app, resources={r"/api/*": {"origins": "*"}})
    # CORS(app, origins=["http://localhost:8081", "http://pmo.test.ur.gov.iq"])
    # CORS(app, resources={r"/api/*": {"origins": "*"}})  # Enable CORS for /api/* routes
    # CORS(app, resources={r"/*": {"origins": "http://localhost"}})
    # CORS(app, resources={r"/*": {"origins": "http://10.92.92.232"}})
    # CORS(app, resources={r"/hello/*": {"origins": "http://localhost"}})
    # CORS(app, resources={r"/*": {"origins": "http://pmo.test.ur.gov.iq"}})
    # app.config.from_object(DevConfig)
    app.config.from_object(config)
    db.init_app(app)
    migrate = Migrate(app,db)
    JWTManager(app)
    api = Api(app, doc='/docs')
##########################################################
    @app.route('/api/hello', methods=['GET'])
    def get():
            try:
                return make_response({'message':"Connected successfully from Goods Inspection"}, 200)
            except:
                    message = {'message': 'There is no connection'}
                    status_code = 500
                    response = make_response(jsonify(message), status_code)
                    return response 


    api.add_namespace(interface_ns)
  
    return app
##########################################################