from flask import jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_restful import Resource, Api, request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

mongo_db-url = "mongodb+srv://Bharani_0408:<password>@crs-database.7drty.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
