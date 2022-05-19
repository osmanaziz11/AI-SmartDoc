import pandas as pd
import numpy as np
import json
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from scipy.stats import mode

dataset_path = "Training.csv"
# final_svm_model=''
# final_nb_model=''
# final_rf_model=''
# encoder=''

def symptoms():
    sym_data = pd.read_csv(dataset_path).drop(['prognosis'],axis=1).dropna(axis=1) #removing last two column
    sym_list=sym_data.columns.values  #Retreive Columns name
    list_of_symptoms = {}
    for index, value in enumerate(sym_list):
        symptom = " ".join([i.capitalize() for i in value.split("_")])
        list_of_symptoms[symptom] = index
    return list_of_symptoms

def main(user_sym):
    dataset_path = "Training.csv"
    data = pd.read_csv(dataset_path).dropna(axis=1)
    # Encoding the target value into numerical
    # value using LabelEncoder
    encoder = LabelEncoder()
    data["prognosis"] = encoder.fit_transform(data["prognosis"])

    # Separate Columns into X and Y
    # X is Symtoms Column 
    X = data.iloc[:,:-1]
    # Y is label column 
    y = data.iloc[:, -1]


    # Buil final model 
    # Training the models on whole data
    final_svm_model = SVC()
    final_nb_model = GaussianNB()
    final_rf_model = RandomForestClassifier(random_state=18)
    final_svm_model.fit(X, y)
    final_nb_model.fit(X, y)
    final_rf_model.fit(X, y)


    # Expecting List of Symptoms
    data_dict = {
    "symptom_index":symptoms(),
    "predictions_classes":encoder.classes_
    }
    input_data = [0] * len(data_dict["symptom_index"])
    for symptom in user_sym:
        index = data_dict["symptom_index"][symptom]
        input_data[index] = 1
    input_data = np.array(input_data).reshape(1,-1)

    # generating individual outputs
    rf_prediction = data_dict["predictions_classes"][final_rf_model.predict(input_data)[0]]
    nb_prediction = data_dict["predictions_classes"][final_nb_model.predict(input_data)[0]]
    svm_prediction = data_dict["predictions_classes"][final_svm_model.predict(input_data)[0]]
     
    # making final prediction by taking mode of all predictions
    final_prediction = mode([rf_prediction, nb_prediction, svm_prediction])[0][0]
    predictions = {
    "rf_model_prediction": rf_prediction,
    "naive_bayes_prediction": nb_prediction,
    "svm_model_prediction": nb_prediction,
    "final_prediction":final_prediction
    }

    return predictions
