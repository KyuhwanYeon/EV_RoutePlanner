# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 15:54:42 2017

@author: Kyuhwan
"""

def CalculateRange(InputType,SOCpercent):
    InputType=int(InputType)
    SOCpercent=int(SOCpercent)
    if InputType == 0: #경차
        EnergyConsumption = 210.99
        BatteryCapacity = 16
    elif InputType == 1: #소형SUV
        EnergyConsumption = 189.35
        BatteryCapacity = 64
    elif InputType == 2: #준중형
        EnergyConsumption = 175.92
        BatteryCapacity = 28
    elif InputType == 3: #버스
        EnergyConsumption = 1059.31
        BatteryCapacity = 256
    elif InputType == 4: #소형트럭
        EnergyConsumption = 316.44
        BatteryCapacity = 17.8
    elif InputType == 5: #상용트럭
        EnergyConsumption = 2484.47    
        BatteryCapacity = 1600

    NowCapacity = SOCpercent*(BatteryCapacity*1000)/100
    RealRange=NowCapacity/EnergyConsumption
    print('Range is calculated')
    return RealRange

print(CalculateRange(1,'28'))