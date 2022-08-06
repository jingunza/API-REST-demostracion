"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def get_users():

    users = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users))

    return jsonify(all_users), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_unit(user_id):

    request_body_user = request.get_json()
    user1 = User.query.get(user_id)
    user1_ser = user1.serialize()

    return jsonify(user1_ser), 200

@app.route('/user', methods=['POST'])
def post_user():

    request_body_user = request.get_json()

    user1 = User(first_name = request_body_user["first_name"], email = request_body_user["email"], password = request_body_user["password"])
    db.session.add(user1)
    db.session.commit()

    return jsonify(request_body_user), 200

@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):

    request_body_user = request.get_json()

    user1 = User.query.get(user_id)
    if user1 is None:
        raise APIException('User not found', status_code=404)
    if "id" in request_body_user:
        user1.id = request_body_user["id"]
    if "first_name" in request_body_user:
        user1.first_name = request_body_user["first_name"]
    if "email" in request_body_user:
        user1.email = request_body_user["email"]
    db.session.commit()

    return jsonify("ok"), 200

@app.route('/user/<int:user_id>', methods=['DELETE'])
def del_user(user_id):

    request_body_user = request.get_json()

    user1 = User.query.get(user_id)
    if user1 is None:
        raise APIException('User not found', status_code=404)
    db.session.delete(user1)
    db.session.commit()

    return jsonify("ok"), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
