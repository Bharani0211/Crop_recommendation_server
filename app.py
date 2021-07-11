from flask import Flask, jsonify, json
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from flask_cors import CORS, cross_origin
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
CORS(app)
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
        if data['email']==None:
            return {"message":"username field is empty"}, 400
        if data['password']==None:
            return {"message":"password field is empty"}, 400
        res = next(filter(lambda x: (x['email']==data['email'] and x['password']== data['password']), users),None)
        if res is None:
            return {"message":"user not found"}, 404
        if data['email']==res['email'] and data['password']==res['password']:
            access_token = create_access_token(identity={"email":res['email']})
            data = {
                "access_token":access_token,
                "_id":str(res['_id']),
                "email":str(res['email']),
                "username":str(res['username']),
                "area":str(res['area']),
                "village_taluk":str(res['village_taluk']),
                "district":str(res['district']),
                "state":str(res['state']),
            }
            response = app.response_class(
                response=json.dumps(data),
                status=200,
                mimetype='application/json'
            )
            return response
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
            "email":data['email'],
            "username":data['username'],
            "password":data['password'],
            "area":data['area'],
            "village_taluk":data['village_taluk'],
            "district":data['district'],
            "state":data['state'],
            "created_at":datetime.fromtimestamp(datetime.timestamp(datetime.now())),
        }

        #inserting user details
        result = db.loginDetails.insert_one(user)
        _id=str(result.inserted_id)

        # creating user in crop database with their _id and name
        crop = {
            "_id":_id,
            "email":data['email'],
            "username":data['username'],
            "history":[],
        }
        database = client['CropResultDatabase']
        result1 = database[_id].insert_one(crop)

        # creating user in feedback database with their _id and name
        feedback = {
            "_id":_id,
            "email":data['email'],
            "username":data['username'],
            "feedbacks":[],
        }
        database = client['Feedbacks']
        result2 = database[_id].insert_one(feedback)

        # creating user in contactUs database with their _id and name
        contactUs = {
            "_id":_id,
            "email":data['email'],
            "username":data['username'],
            "reports":[],
        }
        database = client['ContactUs']
        result3 = database[_id].insert_one(contactUs)


        if (result and (result1 and (result2 and result3))):
            return {"message": "User added succesfully!"}, 200

class Upload(Resource):
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
                "created_at":str(datetime.fromtimestamp(datetime.timestamp(datetime.now()))),
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
        database[id].update_many({'_id': id}, {'$push': {'history': all_results1[0]}})
        return {
            "uploaded":
            {
                "created_at":str(datetime.fromtimestamp(datetime.timestamp(datetime.now()))),
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
        }, 200

class Results(Resource):
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
                "created_at":results[0]['history'][i]["created_at"],
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

class FeedBack(Resource):
    def post(self):
        data = request.get_json()
        database = client["Feedbacks"]
        all_results1=[]
        id = data["_id"]
        all_results1.append(
            {
                "thoughts":data["thoughts"],
                "rating":data["rating"],
            }
        )
        database[id].update_many({'_id': id}, {'$push': {'feedbacks': all_results1[0]}})
        return { "message":"sumbitted"}, 200

class ContactUs(Resource):
    def post(self):
        data = request.get_json()
        database = client["ContactUs"]
        all_results1=[]
        id = data["_id"]
        all_results1.append(
            {
                "name":data["name"],
                "message":data["message"],
            }
        )
        database[id].update_many({'_id': id}, {'$push': {'reports': all_results1[0]}})
        return { "message":"sumbitted"}, 200

api.add_resource(Upload,'/upload/<string:id>/<string:url>')
api.add_resource(Results,'/result')
api.add_resource(SignUp,'/signup')
api.add_resource(Login,'/login')
api.add_resource(FeedBack,'/feedback')
api.add_resource(ContactUs,'/contactus')

if __name__ == '__main__':
    app.run(debug=True)
