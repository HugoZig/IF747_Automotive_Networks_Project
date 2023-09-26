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
import random 
import threading
import statistics as stats
import datetime
import logging
import binascii
from joblib import dump, load

last_timestamp=0

ids = {    #[dp, media, flag, timeStamp]
    162:[0.248626,0.102872,0,0],
    180:[0.248626,0.102872,0,0],
    26:[0.249708,0.102886,0,0],
    423:[0.560754,0.514258,0,0],
    433:[0.560754,0.514258,0,0],
    440:[0.560755,0.514258,0,0],
    443:[0.560736,0.514259,0,0],
    457:[0.560755,0.514258,0,0],
    467:[0.560775,0.514255,0,0], 
    678:[0.793283,1.027960,0,0],
    689:[0.793315,1.027965,0,0],
    699:[0.793283,1.027960,0,0],
    47:[0.249708,0.102886,0,0],
    980:[1.905403,5.135122,0,0],
    990:[5.135123,1.905403,0,0], 
    109:[0.249708,0.102886,0,0],
    141:[0.248627,0.102872,0,0],
    346:[0.560775,0.514255,0,0],
    367:[0.560775,0.514255,0,0],   
    397:[0.560775,0.514255,0,0],
    410:[0.560775,0.514255,0,0],
    36:[0.248603,0.102868,0,0],
    604:[0.793314,1.027965,0,0],
    635:[0.793283,1.027960,0,0],
    668:[0.793315,1.027965,0,0],
    57:[0.248603,0.102868,0,0],
    67:[0.248603,0.102868,0,0],
    1132:[1.905319,5.135111,0,0],
    88:[0.249708,0.102886,0,0],
    98:[0.248616,0.102869,0,0],
    119:[0.248616,0.102869,0,0],
    131:[0.249708,0.102886,0,0],
    152:[0.249708,0.102886,0,0],
    326:[0.560775,0.514255,0,0],
    387:[0.560775,0.514255,0,0],
    408:[0.560775,0.514255,0,0],
    614:[0.793283,1.027960,0,0],
    625:[0.793315,1.027965,0,0],
    646:[0.793315,1.027965,0,0],
    656:[0.793283,1.027960,0,0],
    1056:[1.905319,5.135111,0,0],
    1111:[1.905319,5.135111,0,0],
    1121:[1.905319,5.135111,0,0],
    1143:[0.793283,1.027960,0,0],
    1154:[1.905404,5.135122,0,0]
}


def check_timestamp(timestamp, dp, mean):
    if (mean+5*dp) >= timestamp and (mean-5*dp) <= timestamp:
        return True
    else:
        return False

msgToSend = can.Message(
        arbitration_id=0x0,
        data=[0xA, 0xA, 0xA, 0xA],
        is_extended_id=True)

def generateDfUniques(path):   
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
    return df.drop_duplicates()

df = generateDfUniques('datasets/can-initial.log')
model =  load('model2.joblib') 
print("Modelo foi levantado")
 
logging.basicConfig(filename=f"bus-{datetime.datetime.now()}.log", level=logging.INFO, format='%(message)s')

def createLogLine(msg, type = ""):
    payload = "".join(["{:02X}".format(byte) for byte in msg.data])
    if type != "":
        logging.info(f'({msg.timestamp}) {msg.channel} {hex(msg.arbitration_id)}#{payload} {type}')
    else:
        logging.info(f'({msg.timestamp}) {msg.channel} {hex(msg.arbitration_id)}#{payload}')

with can.Bus(channel="can0", interface="virtual", bitrate=50000) as bus:
   
    for msg in bus:
        arbitration_id = msg.arbitration_id
        data = ids.get(arbitration_id, 0)
        if data:
            if not data[2]:
                createLogLine(msg) #mensagem sem fraudes
                data[2] = 1
            elif (check_timestamp(msg.timestamp - data[3], data[0], data[1])):
                if(bytearray(msg.data).__len__() == 0):
                    print(f"({msg.timestamp}) {msg.channel} {msg.arbitration_id}# E3 => paylod inválido")
                    createLogLine(msg, 'E3')
                    continue
                if((df['CAN ID'] == msg.arbitration_id) & (df['PAYLOAD'] ==  int("".join(["{:02X}".format(byte) for byte in msg.data]), 16 )  )).any():
                    createLogLine(msg) #mensagem sem fraudes  
                    continue
                predictResponse = model.predict(np.array([[msg.arbitration_id, int("".join(["{:02X}".format(byte) for byte in msg.data]), 16 )]]).reshape(1, -1) )
                if predictResponse[0] == -1: # anomalia detectada
                    print(f"({msg.timestamp}) {msg.channel} {msg.arbitration_id}#{''.join(['{:02X}'.format(byte) for byte in msg.data])} E2 => anomalia detectada")
                    createLogLine(msg, 'E2')
                    bus.send(msgToSend)
                else:
                    createLogLine(msg) #mensagem sem fraudes
                pass
            else: 
                print(f"({msg.timestamp}) {msg.channel} {msg.arbitration_id}#{''.join(['{:02X}'.format(byte) for byte in msg.data])} E0 => timestamp malicioso")
                createLogLine(msg, 'E0')
                bus.send(msgToSend)
            data[3] = msg.timestamp
            ids.update({arbitration_id:data})
        else: 
            print(f"({msg.timestamp}) {msg.channel} {msg.arbitration_id}#{''.join(['{:02X}'.format(byte) for byte in msg.data])} E1 => ID inexistente") 
            createLogLine(msg, 'E1')
            bus.send(msgToSend)