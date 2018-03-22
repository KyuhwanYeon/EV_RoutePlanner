# -*- coding: utf-8 -*-
'''
Created on Sat Nov 18 10:18:55 2017
@author:Kyuhwan Yeon
'''

import googlemaps
from datetime import datetime
import time
from math import sin, cos, sqrt, atan2, radians
import folium
from folium.plugins import Draw
import numpy as np
import sys
import csv
import polyline
from PyQt5.QtWidgets import QApplication, QMainWindow, QLCDNumber, QTextBrowser
from PyQt5 import uic
from PyQt5.QtCore import QUrl
from CalculateSOCtoRange import CalculateRange


#%%
form_class = uic.loadUiType("RoutePlannerUI.ui")[0]


class gui(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        #self.view = QWebView.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("Route planner")
        self.pushButton.clicked.connect(self.btn_clicked)
        self.pushButton_2.clicked.connect(self.btn_clicked2)
        self.pushButton_3.clicked.connect(self.btn_clicked3)

        
        self.progressBar.setValue(0)
        
             
    def btn_clicked(self):
        self.progressBar.setValue(0)
        start = self.lineEdit.text()
        end = self.lineEdit_2.text()
        radius = CalculateRange(self.comboBox.currentIndex(),self.lineEdit_3.text())
        print(self.lineEdit_3.text())

        self.lcdNumber.display(radius)
        
        if not (0 <= float(self.lineEdit_3.text()) <= 100):
            self.textBrowser.append("Please write SOC 0 to 100")
        else:

            self.textBrowser.append("Route is generated")  
            self.mapping(start,end,radius,1)
            self.webView.setUrl(QUrl('temp\RoutePlanner.html'))
            self.webView.reload()
        self.progressBar.setValue(100)
        
    def btn_clicked2(self):
        self.progressBar.setValue(0)
        start = self.lineEdit.text()
        end = self.lineEdit_2.text()

        radius = CalculateRange(self.comboBox.currentIndex(),self.lineEdit_3.text())

        
        if not (0 <= float(self.lineEdit_3.text()) <= 100):
            self.textBrowser.append("Please write SOC 0 to 100")
        else:
            self.textBrowser.append("Available Chargers are displayed")
            self.mapping(start,end,radius,2)
            self.webView.setUrl(QUrl('temp\RoutePlanner.html'))
            self.webView.reload()
        self.progressBar.setValue(100)
        
    def btn_clicked3(self):
        self.progressBar.setValue(0)
        start = self.lineEdit.text()
        end = self.lineEdit_2.text()
        radius = CalculateRange(self.comboBox.currentIndex(),self.lineEdit_3.text())
        if not (0 <= float(self.lineEdit_3.text()) <= 100):
            self.textBrowser.append("Please write SOC 0 to 100")
        else:
            self.textBrowser.append("Route is generated") 
            self.mapping(start,end,radius,3)
            self.webView.setUrl(QUrl('temp\RoutePlanner.html'))
            self.webView.reload()
        self.progressBar.setValue(100)

    def mapping(self,start,end,dis,arg):
        gmaps = googlemaps.Client(key='AIzaSyBjcH8wXlR_EZAIm8k8XFHgkJ6cOlEtpvM')
        now = datetime.now()

        directions_result = gmaps.directions(start,
                                             end,
                                             mode="driving",
                                             departure_time=now)
        
        DirectionResult=directions_result[0]['legs']
        DirectionSteps=DirectionResult[0]['steps']
        DecodedNp = np.zeros(shape=[1,2])
        
        for step in DirectionSteps:   
            Temp = list(step['polyline'].values())
            DecodedNp=np.concatenate((DecodedNp,np.array(polyline.decode(Temp[0]))))
            
        DecodedPos = DecodedNp.tolist()
        
        m = folium.Map(location=DecodedPos[1], zoom_start=5,tiles="Stamen Toner")
        
        
        
        draw = Draw()
        draw.add_to(m) # 그림기능
        
        #folium.TileLayer('Mapbox Control Room').add_to(m) # 여러가지 타일들 "Mapbox Bright"
        #folium.TileLayer('Stamen Toner').add_to(m)
        #folium.TileLayer('openstreetmap').add_to(m) 
        #folium.LayerControl().add_to(m) # 빠른 마커로딩과 동시에 안됨
        convert_dis = dis
        try:
            convert_dis=float(convert_dis)
        except ValueError:
            pass


         
        
        
        if arg == 1:
            if convert_dis*1000 < DirectionResult[0]['distance']['value']:
                folium.Circle(location = DecodedPos[1], popup='Available distance', radius=convert_dis*1000,    color='#8AC317',fill=True,fill_color='#BBFF33').add_to(m)#기본 길이단위 미터   

            ShortestPolyline = folium.PolyLine(locations=[DecodedPos[1:]],color='red',weight=5).add_to(m)
            attr = {'fill': '#421100', 'font-weight': 'bold', 'font-size': '48'}
            folium.plugins.PolyLineTextPath(ShortestPolyline,text='\u00BB    ',repeat=True,center = True,
                    offset=16,attributes=attr).add_to(m) # 색깔 그림 폰트 등등 라인꾸미기
       
            self.progressBar.setValue(50)
            
        elif arg == 2:
            folium.Circle(location = DecodedPos[1], popup='Available distance', radius=convert_dis*1000,    color='#8AC317',fill=True,fill_color='#BBFF33').add_to(m)#기본 길이단위 미터   
        
            self.progressBar.setValue(0)
            EV_data = self.EV_Discovery()
            Availiable_ChargerLocList = []
            for i in range(len(EV_data)):
                Charger_distance = self.Distance(DecodedPos[1][0],DecodedPos[1][1],EV_data[i][0],EV_data[i][1])
                if Charger_distance < convert_dis:
                    Availiable_ChargerLocList.append(EV_data[i])
            folium.plugins.FastMarkerCluster(Availiable_ChargerLocList).add_to(m)
            if len(Availiable_ChargerLocList) == 0:
                self.textBrowser.append("There are no availiable charger")
                self.progressBar.setValue(100)
        elif arg == 3:
            folium.Circle(location = DecodedPos[1], popup='Available distance', radius=convert_dis*1000,    color='#8AC317',fill=True,fill_color='#BBFF33').add_to(m)#기본 길이단위 미터   
        
            self.progressBar.setValue(0)
            EV_data = self.EV_Discovery()
            Availiable_ChargerLocList = []
            for i in range(len(EV_data)):
                Charger_distance = self.Distance(DecodedPos[1][0],DecodedPos[1][1],EV_data[i][0],EV_data[i][1])

                if Charger_distance < convert_dis:
                    Availiable_ChargerLocList.append(EV_data[i])
            print(len(Availiable_ChargerLocList))
            if len(Availiable_ChargerLocList) == 0:
                if convert_dis*1000 < DirectionResult[0]['distance']['value']:
                    folium.Circle(location = DecodedPos[1], popup='Available distance', radius=convert_dis*1000,    color='#8AC317',fill=True,fill_color='#BBFF33').add_to(m)#기본 길이단위 미터   
    
                ShortestPolyline = folium.PolyLine(locations=[DecodedPos[1:]],color='red',weight=5).add_to(m)
                attr = {'fill': '#421100', 'font-weight': 'bold', 'font-size': '48'}
                folium.plugins.PolyLineTextPath(ShortestPolyline,text='\u00BB    ',repeat=True,center = True,
                        offset=16,attributes=attr).add_to(m) # 색깔 그림 폰트 등등 라인꾸미기
           
                self.progressBar.setValue(50)
       
                    
                self.textBrowser.append("There are no availiable charger")

            else:
                self.progressBar.setValue(70)        
                #Find Efficient Electric Charger location
                min_Dist = 10000000000 # Initial min value
                Efficient_ElecChargLoc = []
                for i in range(len(Availiable_ChargerLocList)):
                    Dist1=self.Distance(DecodedPos[1][0],DecodedPos[1][1],Availiable_ChargerLocList[i][0],Availiable_ChargerLocList[i][1])
                    Dist2=self.Distance(DecodedPos[-1][0],DecodedPos[-1][1],Availiable_ChargerLocList[i][0],Availiable_ChargerLocList[i][1])
                    if (Dist1+Dist2<min_Dist):
                        min_Dist = Dist1+Dist2
                        Efficient_ElecChargLoc = [Availiable_ChargerLocList[i][0],Availiable_ChargerLocList[i][1]]
                print(Efficient_ElecChargLoc)
                self.progressBar.setValue(80)   
                folium.Marker(Efficient_ElecChargLoc, popup='Recommended Electric Charger',icon=folium.Icon(color='green')).add_to(m)
                
                reverse_geocode_result = gmaps.reverse_geocode(Efficient_ElecChargLoc)
                ElecLocStr=reverse_geocode_result[0]['formatted_address']
                
                
                #Start to Electric charger            
                directions_result = gmaps.directions(start,ElecLocStr, mode="driving", departure_time=now)     
                DirectionResult=directions_result[0]['legs']
                DirectionSteps=DirectionResult[0]['steps']
                DecodedNp = np.zeros(shape=[1,2])        
                for step in DirectionSteps:
                    Temp = list(step['polyline'].values())
                    DecodedNp=np.concatenate((DecodedNp,np.array(polyline.decode(Temp[0]))))            
                DecodedPos = DecodedNp.tolist()  
                StartToElecCharg = folium.PolyLine(locations=[DecodedPos[1:]],color='green',weight=5).add_to(m)    
                attr = {'fill': '#421100', 'font-weight': 'bold', 'font-size': '48'}
                folium.plugins.PolyLineTextPath(StartToElecCharg,text='\u00BB    ',repeat=True,center = True,
                        offset=16,attributes=attr).add_to(m) # 색깔 그림 폰트 등등 라인꾸미기    
    
                #Electric charger to end
                directions_result = gmaps.directions(ElecLocStr,end, mode="driving", departure_time=now)     
                DirectionResult=directions_result[0]['legs']
                DirectionSteps=DirectionResult[0]['steps']
                DecodedNp = np.zeros(shape=[1,2])        
                for step in DirectionSteps:
                    Temp = list(step['polyline'].values())
                    DecodedNp=np.concatenate((DecodedNp,np.array(polyline.decode(Temp[0]))))            
                DecodedPos = DecodedNp.tolist()  
                ElecChargToEnd = folium.PolyLine(locations=[DecodedPos[1:]],color='green',weight=5).add_to(m)
                attr = {'fill': '#421100', 'font-weight': 'bold', 'font-size': '48'}
                folium.plugins.PolyLineTextPath(ElecChargToEnd,text='\u00BB    ',repeat=True,center = True,
                        offset=16,attributes=attr).add_to(m) # 색깔 그림 폰트 등등 라인꾸미기
                '''
                marker_cluster = folium.plugins.MarkerCluster(
                locations=data, popups=['lon:{}<br>lat:{}'.format(lon, lat) for (lat, lon) in data],
                name='EVcharger',overlay=True,control=False,icon_create_function=None)
                marker_cluster.add_to(m)# 너무 느려서 봉인(여러가지 설정 가능한 마커)
                '''

        
        
#        self.progressBar.setValue(70)
        m.save('temp\RoutePlanner.html')
        
    def EV_Discovery(self):
        matrix = []
        f = open('EVCharger.csv', 'r')
        csv_temp = csv.reader(f)
        
        for row in csv_temp:
            matrix.append(row)
            
        EV = [[] for i in matrix]
        
        for i in range(len(matrix)):
                if i != 0:
                    EV[i].append(float(matrix[i][24]))
                    EV[i].append(float(matrix[i][25]))
        
        del EV[0]
        
        f.close()
            
        return EV
    
    def Distance(self,latitude1,longitude1,latitude2,longitude2):       
        R = 6373.0 
        lat1 = radians(latitude1)
        lat2 = radians(latitude2)
        lon1 = radians(longitude1)
        lon2 = radians(longitude2)
        dlon=lon2-lon1
        dlat=lat2-lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a)) 
        return (R*c)
    
 


        


#%%

if __name__ == "__main__":
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
        app.aboutToQuit.connect(app.deleteLater)    
    gui= gui()
    
    gui.show() 
    app.exec_()
 
    


