import numpy as np
import pandas as pd
import pickle
from flask import Flask
from flask_restful import Api,Resource,reqparse
from googletrans import Translator

translator = Translator()

app=Flask(__name__)
api=Api(app)


class Model():

    def __init__(self):
        with open("dt.pickle", "rb") as file:
            self.model = pickle.load(file)
        self.X = np.zeros(131)
        self.recent = 0
        self.data = pd.read_csv("pre_train_data.csv")
        self.data = self.data.drop('Unnamed: 0', axis=1)
        self.name_feature = list(self.data)
        self.description = pd.read_csv("symptom_Description.csv")
        self.precaution = pd.read_csv('symptom_precaution.csv')
        self.now = 0
        self.decision_tree = self.model.estimators_[self.now]
        self.visited = np.zeros(131)
        self.n_nodes = self.decision_tree.tree_.node_count
        self.children_left = self.decision_tree.tree_.children_left
        self.children_right = self.decision_tree.tree_.children_right
        self.feature = self.decision_tree.tree_.feature
        self.threshold = self.decision_tree.tree_.threshold
        self.node_depth = np.zeros(shape=self.n_nodes, dtype=np.int64)
        self.is_leaves = np.zeros(shape=self.n_nodes, dtype=bool)
        self.stack = [(0, -1)]
        while len(self.stack) > 0:
            node_id, parent_depth = self.stack.pop()
            self.node_depth[node_id] = parent_depth + 1
            if (self.children_left[node_id] != self.children_right[node_id]):
                self.stack.append((self.children_left[node_id], parent_depth + 1))
                self.stack.append((self.children_right[node_id], parent_depth + 1))
            else:
                self.is_leaves[node_id] = True

    def procesing(self, input):
        if input == 2:
            message = self.name_feature[int(self.feature[self.recent])]
            try:
                message = 'Bạn có ' + translator.translate(message.replace('_', " "), src='en',
                                                           dest='vi').text + " không?"
            except:
                message = "Bạn có " + message.replace('_', " ") + " không?"
            return {"message": message, "end": False}

        elif input == 0 or input == 1:
            #if (self.visited[int(self.feature[self.recent])] == 1):
                #x = self.X[self.feature[self.recent]]
            #else:
                #x = int(input)
            x = int(input)
            if(x > self.threshold[self.recent]):
                self.X[int(self.feature[self.recent])] = 1
            self.visited[int(self.feature[self.recent])] = 1
            while(self.visited[int(self.feature[self.recent])] == 1):
                x = self.X[self.feature[self.recent]]
                if (x < self.threshold[self.recent]):
                    self.recent = int(self.children_left[self.recent])
                else:
                    self.recent = int(self.children_right[self.recent])
                if int(self.is_leaves[self.recent]) == True:
                    self.now += 1
                    if (self.now < 16):
                        self.decision_tree = self.model.estimators_[self.now]
                        self.recent = 0
                        self.n_nodes = self.decision_tree.tree_.node_count
                        self.children_left = self.decision_tree.tree_.children_left
                        self.children_right = self.decision_tree.tree_.children_right
                        self.feature = self.decision_tree.tree_.feature
                        self.threshold = self.decision_tree.tree_.threshold
                        self.node_depth = np.zeros(shape=self.n_nodes, dtype=np.int64)
                        self.is_leaves = np.zeros(shape=self.n_nodes, dtype=bool)
                        self.stack = [(0, -1)]
                        while len(self.stack) > 0:
                            node_id, parent_depth = self.stack.pop()
                            self.node_depth[node_id] = parent_depth + 1
                            if (self.children_left[node_id] != self.children_right[node_id]):
                                self.stack.append((self.children_left[node_id], parent_depth + 1))
                                self.stack.append((self.children_right[node_id], parent_depth + 1))
                            else:
                                self.is_leaves[node_id] = True
                    if self.now == 8:
                        a = self.model.predict(self.X.reshape(1, -1))
                        diseases=a[0]
                        des=self.getdescription(a[0])
                        precau=self.getprecaution(a[0])

                        try:
                            diseases = diseases+" / "+translator.translate(diseases.replace('_', " "), src='en', dest='vi').text
                        except:
                            diseases = diseases.replace('_', " ")
                        try:
                            des = translator.translate(des.replace('_', " "), src='en', dest='vi').text
                            precau = translator.translate(precau.replace('_', " "), src='en', dest='vi').text
                        except:
                            diseases = diseases.replace('_', " ")
                            precau=precau.replace('_', " ")
                        message="Chẩn đoán bệnh: "+diseases+" \n Triệu chứng: "+des+" \n Cách xử lí: "+precau
                        return {"message": message,"end": False}
                    elif self.now == 16:
                        a = self.model.predict(self.X.reshape(1, -1))
                        diseases = a[0]
                        des = self.getdescription(a[0])
                        precau = self.getprecaution(a[0])

                        try:
                            diseases = diseases + " / " + translator.translate(diseases.replace('_', " "), src='en',
                                                                               dest='vi').text
                        except:
                            diseases = diseases.replace('_', " ")
                        try:
                            des = translator.translate(des.replace('_', " "), src='en', dest='vi').text
                            precau = translator.translate(precau.replace('_', " "), src='en', dest='vi').text
                        except:
                            diseases = diseases.replace('_', " ")
                            precau = precau.replace('_', " ")
                        message = "Chẩn đoán bệnh: " + diseases + " \n Triệu chứng: " + des + " \n Cách xử lí: " + precau
                        return {"message": message,"end": True}
            message = self.name_feature[int(self.feature[self.recent])]
            try:
                message ='Bạn có '+ translator.translate(message.replace('_', " "), src='en', dest='vi').text+" không?"
            except:
                message = "Bạn có "+message.replace('_', " ")+" không?"
            return {"message": message, "end": False}

        else:
            return {}

    def getdescription(self, name):
        for i in range(len(self.description)):
            if name in self.description['Disease'].iloc[i]:
                return self.description['Description'].iloc[i]
        return "Not found"

    def getprecaution(self, name):
        for i in range(len(self.precaution)):
            if name in self.precaution['Disease'].iloc[i]:
                return (self.precaution['Precaution_1'].iloc[i] + ", "
                        + self.precaution['Precaution_2'].iloc[i] + ", "
                        + self.precaution['Precaution_3'].iloc[i] + ", "
                        + self.precaution['Precaution_4'].iloc[i])
        return "Not found"


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



