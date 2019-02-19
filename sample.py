import matplotlib
matplotlib.use('Agg')
import csv
import pylab
import numpy as np
import uuid
import pymysql
from numpy import vstack,array
from scipy.cluster.vq import *
from flask import Flask,render_template,request

#Connection parameters to the Host in Azure and the Database MYSQL in AZURE
hostname = ''
username = ''
password = '3'
database = ''
myConnection = pymysql.connect( host=hostname, user=username, passwd=password, db=database, cursorclass=pymysql.cursors.DictCursor, local_infile=True)
#Establish connection with Pymysql connector
print 'DB connected'

app = Flask(__name__,template_folder="static")

coloumn_names = ["Subject","CourseNumber","SectionNumber","ClassNumber","M","T","W","Th","F","Sa","Su","DepartmentalApproval","MaxEnroll"]

myfile = open("CSEFall2018.csv","r")
csv_reader = csv.DictReader(myfile, fieldnames=coloumn_names)
next(csv_reader)

@app.route('/')
def index():
  return render_template('welcome.html')

@app.route('/login', methods=['GET','POST'])
def login():
	 user_name = request.form['uname']
	 password = request.form['passwd']
	 cur = myConnection.cursor()
	 cur.execute("select COUNT(1) from Students where GivenName =  %s;", [user_name])
	 if cur.fetchall()[0]:
            cur.execute("SELECT Password FROM Students WHERE GivenName = %s;", [user_name]) 
            for row in cur.fetchall():
                if password == row['Password']:
		     r1 = cur.execute("select Surname,GivenName,StreetAddress from Students where GivenName = %s;",[user_name])
		     cur.fetchall()
                     return render_template('index.html',cuser=user_name,cn = r1)
                else:
                    error = "Invalid Credential"
		    return render_template('failure.html',cuser=user_name)

         else:
             error = "Invalid Credential"
	     return render_template('failure.html',cuser=user_name)


mylist = []
@app.route('/kmeans', methods=['GET', 'POST'])
def main():
        attribute1 = request.form['attribute1']
        attribute2 = request.form['attribute2']
        clusters = request.form['clusters']
        K_clusters = int(clusters)
        mylist = getdata(attribute1,attribute2)
        data = []
        cdist=[]
        data = array(mylist)
        cent, pts = kmeans2(data,K_clusters)
        print pts
        disCluster = []
        for i in range(len(cent)):
            x1 = cent[i][0]
            y1 = cent[i][1]
            x1 = float("{0:.3f}".format(x1))
            y1 = float("{0:.3f}".format(y1))

            for j in range(i+1,len(cent)):
                dc = {}
                x2 = cent[j][0]
                y2 = cent[j][1]
                x2 = float("{0:.3f}".format(x2))
                y2 = float("{0:.3f}".format(y2))
                dist = np.sqrt((x1-x2)*2 + (y1-y2)*2)
                cdist.append(dist)
                dc['dist'] = "Distance between cluster " + str(i) + " and cluster " + str(j) + " is: " + str(dist)
                disCluster.append(dc)
                print (disCluster)
                print ("Distance between cluster " + str(i) + " and cluster " + str(j) + " is: " + str(dist))
        clr = ([1, 1, 0.0], [0.2, 1, 0.2], [1, 0.2, 0.2], [0.3, 0.3, 1],[0.0, 1.0, 1.0], [0.6, 0.6, 0.1], [1.0, 0.5, 0.0], [1.0, 0.0, 1.0], [0.6, 0.2, 0.2], [0.1, 0.6, 0.6], [0.0, 0.0, 0.0], [0.8, 1.0, 1.0], [0.70, 0.50, 0.50], [0.5, 0.5, 0.5], [0.77, 0.70, 0.00])
        colors = ([(clr)[i] for i in pts])
        print colors
        print pts
        clr_dict = {"yellow":0,"green":0,"red":0,"blue":0,"cyan":0,"deepolive":0,"orange":0,"magenta":0,"ruby":0,"deepteal":0,"black":0,"palecyan":0,"dirtyviolet":0,"gray":0,"olive":0}
        pdict=[]
        for x in colors:
            if str(x) == "[1, 1, 0.0]":
                clr_dict["yellow"] += 1
            if str(x) == "[0.2, 1, 0.2]":
                clr_dict["green"] += 1
            if str(x) == "[1, 0.2, 0.2]":
                clr_dict["red"] += 1
            if str(x) == "[0.3, 0.3, 1]":
                clr_dict["blue"] += 1
            if str(x) == "[0.0, 1.0, 1.0]":
                clr_dict["cyan"] += 1
            if str(x) == "[0.6, 0.6, 0.1]":
                clr_dict["deepolive"] += 1
            if str(x) == "[1.0, 0.5, 0.0]":
                clr_dict["orange"] += 1
            if str(x) == "[1.0, 0.0, 1.0]":
                clr_dict["magenta"] += 1
            if str(x) == "[0.6, 0.2, 0.2]":
                clr_dict["ruby"] += 1
            if str(x) == "[0.1, 0.6, 0.6]":
                clr_dict["deepteal"] += 1
            if str(x) == "[0.0, 0.0, 0.0]":
                clr_dict["black"] += 1
            if str(x) == "[0.8, 1.0, 1.0]":
                clr_dict["palecyan"] += 1
            if str(x) == "[0.70, 0.50, 0.50]":
                clr_dict["dirtyviolet"] += 1
            if str(x) == "[0.5, 0.5, 0.5]":
                clr_dict["gray"] += 1
            if str(x) == "[0.77, 0.70, 0.00]":
                clr_dict["olive"] += 1

        f_write='Cluster,Count\r\n'
        cnt=0
        print (clr_dict)
        for i in clr_dict:
            if clr_dict[i] == 0:
                continue
            string = str(cnt) + " : " + str(clr_dict[i])
            pdict.append(string)
            print ("No of points in cluster with " + str(i) + " is: " + str(clr_dict[i]))
            f_write+= str(cnt)+','+str(clr_dict[i])+'\r\n'
            cnt += 1
        with open("static/d3chart.csv",'wb') as nfile:
            nfile.write(f_write.encode("utf-8"))
        pylab.scatter(data[:,0],data[:,1], c=colors)
        pylab.scatter(cent[:,0],cent[:,1], marker='o', s = 400, linewidths=3, c='none')
        pylab.scatter(cent[:,0],cent[:,1], marker='x', s = 400, linewidths=3)

        pylab.savefig("static/kmeans1221.png")

        return render_template('index.html',cdist=cdist,pdict=pdict, disCluster = disCluster)

def getdata(attr1,attr2):
    c = 0
    for row in csv_reader:
        c += 1
        if c == 25000:
            break
        pair = []
        if row[attr1] == "":
            row[attr1] = 0
        if row[attr2] == "":
            row[attr2] = 0
        x = float(row[attr1])
        y = float(row[attr2])
        pair.append(x)
        pair.append(y)
        mylist.append(pair)
        print pair
    return mylist


@app.route('/show', methods=['GET', 'POST'])
def show():
  return render_template('show.html')

@app.route('/Bargraph', methods=['GET', 'POST'])
def bargraph():
  return render_template('d3barchart.html')

@app.route('/Piegraph', methods=['GET', 'POST'])
def Piegraph():
  return render_template('d3piechart.html')



if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')