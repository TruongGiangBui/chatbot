import numpy as np
import pandas as pd
import pickle

global children_left
global children_right
global feature
global is_leaves
global name_feature1
global name_feature

global node_depth
global threshold
global model
global X
global recent
global builded
builded=False






from flask import Flask
from flask_restful import Api,Resource,reqparse


app=Flask(__name__)
api=Api(app)


class ChatBot(Resource):


    def get(self,input):
        global children_left
        global children_right
        global feature
        global is_leaves
        global name_feature1
        global name_feature

        global node_depth
        global threshold
        global model
        global X
        global recent
        global builded

        if int(input)==2 and builded==False:
            builded=True
            children_left = np.loadtxt("chidlren_left.csv")
            children_right = np.loadtxt("chidlren_right.csv")
            feature = np.loadtxt("feture.csv")
            is_leaves = np.loadtxt("is_leaves.csv")
            name_feature1 = pd.read_csv("name_feature.csv")
            name_feature = np.array(name_feature1)
            name_feature = name_feature.reshape(1, -1)
            name_feature = name_feature.reshape(131)
            node_depth = np.loadtxt("node_depth.csv")
            threshold = np.loadtxt("threshold.csv")
            with open("dt.pickle", "rb") as file:
                model = pickle.load(file)

            X = np.zeros(131)
            recent = 0

            message=name_feature[int(feature[recent])]
            return {"message":message,"end":False}
        else:

            args = chat.parse_args()
            x = int(input)
            if (x < threshold[recent]):
                recent = int(children_left[recent])
            else:
                X[int(feature[recent])] = 1
                recent = int(children_right[recent])
            if int(is_leaves[recent]) != 1:
                message = name_feature[int(feature[recent])]
                return {"message": message,  "end": False}
            else:
                a = model.predict(X.reshape(1, -1))
                return {"message": a[0], "end": True}

    


api.add_resource(ChatBot,"/chat/<string:input>")
if __name__=="__main__":
    app.run(debug=True)