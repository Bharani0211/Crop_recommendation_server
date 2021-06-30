from flask import Flask, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
from flask_restful import Resource, Api, request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from knn_prediction.knn_index import knn_prediction_algorithm
from decision_tree.dt_index import decision_tree_algorithm
from naive_bayes.nb_index import naive_bayes_algorithm
from random_forest.rf_index import random_forest_algorithm
from logistic_regression.lr_index import logistic_regression_algorithm


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'S243t154shd$gu/adafhfj*jhDSHHDfbbfamfj_dAJDA.VVFAEF766r6^&'
jwt = JWTManager(app)
api = Api(app)


# DB data initialisation

client = MongoClient()
client = MongoClient("mongodb+srv://admin:admin@cluster0.7drty.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
print("Mongodb connection succesfull")

db = client['UserAuthData']
class Login(Resource):
    def post(self):
        data = request.get_json()
        users = db.loginDetails.find()
        if data['username']==None:
            return {"message":"username field is empty"}, 400
        if data['password']==None:
            return {"message":"password field is empty"}, 400
        res = next(filter(lambda x: (x['username']==data['username'] and x['password']== data['password']), users),None)
        if res is None:
            return {"message":"user not found"}, 404
        if data['username']==res['username'] and data['password']==res['password']:
            access_token = create_access_token(identity={"username":res['username']})
            ress = {
                "access_token":access_token,
                "_id":str(res['_id'])
            }
            return ress
        else:
            return {"message":"Invalid login credentials"}, 400

class SignUp(Resource):
    def post(self):
        data = request.get_json()
        users = db.loginDetails.find()
        res = next(filter(lambda x: (x['username']==data['username'] and x['password']== data['password']), users),None)
        if res is not(None):
            return {"message":"user with this username is already found"}, 404
        user = {
            "username":data['username'],
            "password":data['password'],
            "area":data['area'],
            "village_taluk":data['village_taluk'],
            "district":data['district'],
            "state":data['state'],
        }

        #inserting user details
        result = db.loginDetails.insert_one(user)
        
        _id=str(result.inserted_id)
        # creating user in crop database with their _id and name
        crop = {
            "_id":_id,
            "username":data['username'],
            "history":[],
        }
        database = client['CropResultDatabase']
        result1 = database[_id].insert_one(crop)


        if result and result1:
            return {"message": "User added succesfully!"}, 200

class Upload(Resource):
    @jwt_required()
    def post(self, id, url):
        all_results1=[]
        link='https://drive.google.com/file/d/'+url+'/view?usp=sharing'
        print(link)
        # link='https://drive.google.com/file/d/1YSn5_UADWhx8wLf4GwKgYJ6VWs85L5eb/view?usp=sharing'
        nb=naive_bayes_algorithm(link)
        knn=knn_prediction_algorithm(link)
        dt=decision_tree_algorithm(link)
        rf=random_forest_algorithm(link)
        lr=logistic_regression_algorithm(link)

        all_results1.append(
            {
                "data":[
                    {
                        "naive_bayes":{
                            "crop":nb["Crop"],
                            "accuracy":nb["Percentage"]+"%"
                        },
                    },
                    {
                        "knn":{
                            "crop":knn["Crop"],
                            "accuracy":knn["Percentage"]+"%"
                        },
                    },
                    {
                        "decision_tree":{
                            "crop":dt["Crop"],
                            "accuracy":dt["Percentage"]+"%"
                        }
                    },
                    {
                        "random_forest":{
                            "crop":rf["Crop"],
                            "accuracy":rf["Percentage"]+"%"
                        }
                    },
                    {
                        "logistic_regression":{
                            "crop":lr["Crop"],
                            "accuracy":lr["Percentage"]+"%"
                        }
                    }
                ]
            }
        )
        database = client['CropResultDatabase']
        database[id].update({'_id': id}, {'$push': {'history': all_results1[0]}})
        return {"message":"Uploaded"}, 200

class Results(Resource):
    @jwt_required()
    def get(self):
        data = request.get_json()
        database = client['CropResultDatabase']
        _id=data["id"]
        history = []
        results = database[_id].find()
        length=len(results[0]['history'])
        print(length)
        for i in range(0,length):
            history.append({
                "data":[
                    {
                        "naive_bayes":{
                            "crop":results[0]['history'][i]['data'][0]['naive_bayes']['crop'],
                            "accuracy":results[0]['history'][i]['data'][0]['naive_bayes']['accuracy']
                        }
                    },
                    {
                        "knn":{
                            "crop":results[0]['history'][i]['data'][1]['knn']['crop'],
                            "accuracy":results[0]['history'][i]['data'][1]['knn']['accuracy']
                        }
                    },
                    {
                        "decision_tree":{
                            "crop":results[0]['history'][i]['data'][2]['decision_tree']['crop'],
                            "accuracy":results[0]['history'][i]['data'][2]['decision_tree']['accuracy']
                        }
                    },
                    {
                        "random_forest":{
                            "crop":results[0]['history'][i]['data'][3]['random_forest']['crop'],
                            "accuracy":results[0]['history'][i]['data'][3]['random_forest']['accuracy']
                        }
                    },
                    {
                        "logistic_regression":{
                            "crop":results[0]['history'][i]['data'][4]['logistic_regression']['crop'],
                            "accuracy":results[0]['history'][i]['data'][4]['logistic_regression']['accuracy']
                        }
                    },
                ]
            })
        if len(history) == 0:
            return {"message":"no datas found"}, 404
        return history, 200

api.add_resource(Upload,'/upload/<string:id>/<string:url>')
api.add_resource(Results,'/result')
api.add_resource(SignUp,'/signup')
api.add_resource(Login,'/login')

if __name__ == '__main__':
    app.run(debug=True)
