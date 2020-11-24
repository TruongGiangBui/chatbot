import numpy as np
import pandas as pd
import pickle
from flask import Flask
from flask_restful import Api,Resource,reqparse


app=Flask(__name__)
api=Api(app)


class Model():
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

    def __init__(self):
        with open("dt.pickle", "rb") as file:
            self.model = pickle.load(file)
        self.X = np.zeros(131)
        self.recent = 0
    def procesing(self,input):
        if input==2:
            message = self.name_feature[int(self.feature[self.recent])]
            return {"message": message, "end": False}
        else:
            x = int(input)
            if (x < self.threshold[self.recent]):
                self.recent = int(self.children_left[self.recent])
            else:
                self.X[int(self.feature[self.recent])] = 1
                self.recent = int(self.children_right[self.recent])
            if int(self.is_leaves[self.recent]) != 1:
                message = self.name_feature[int(self.feature[self.recent])]
                return {"message": message, "end": False}
            else:
                a = self.model.predict(self.X.reshape(1, -1))
                return {"message": a[0], "end": True}



class ChatBot(Resource):
    def get(self,input):
        global model
        if int(input)==2:
            model=Model()
            return model.procesing(2);
        else:
            return model.procesing(int(input))

api.add_resource(ChatBot,"/chat/<string:input>")
if __name__=="__main__":
    app.run(debug=True)
    
