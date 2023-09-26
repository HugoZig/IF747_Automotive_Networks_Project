# Sistema de defesa de uma rede CAN
# Redes Automotivas 2023.1 - CIn UFPE

import can
import numpy as np
import pandas as pd
import math
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.ensemble import IsolationForest
import random 
import threading
import statistics as stats
import datetime
import logging
import binascii
from joblib import dump, load


def generateModel(path):   
    def adjustPayload(x): 
        if x == "R" or x == "T":
            x = 0
        if x == "NaN" or (type(x) is float and math.isnan(x) ) :
            x = 0 #np.nan
        elif x != np.nan and (type(x) is str):
            x = int(x, 16)
        return x

    df = pd.read_csv(path, sep=' |#', engine='python')
    df.columns = ["Timestamp", "BUS", "CAN ID", "PAYLOAD"]
    df["Timestamp"] = df["Timestamp"].apply(lambda x: float(str(x).replace('(','').replace(')','') ))
    df = df.drop(columns="Timestamp")
    df["CAN ID"] = df["CAN ID"].apply(lambda x: int(x, 16))
    df = df.drop(columns="BUS")
    
    for column in df.columns:
        if "PAYLOAD" in column:
            df[column] = df[column].apply(lambda x: adjustPayload(x))

    def removeNaNValues(x): 
        if (type(x) is float and math.isnan(x) ) :
            x = 0 
        return x
    df = df.apply(lambda x: removeNaNValues(x) )
 
    #model = LocalOutlierFactor(novelty=True, n_neighbors=20, contamination= 0.01)
    model = OneClassSVM(gamma='auto')
    #model = IsolationForest(n_estimators=100,  max_samples='auto', contamination=0.1)
    model.fit(df.values)
    dump(model, 'model3.joblib') 

    #df['scores']=model.decision_function(df )
    #df['anomaly']=model.predict(df.drop(columns="scores"))
    return model, df

model, df = generateModel('datasets/can-initial.log') 
print("Modelo gerado")
