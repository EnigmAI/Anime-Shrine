import numpy as np
import pandas as pd
import random
import re
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from urllib.parse import urlparse
from uuid import uuid4
import requests
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

def get_index_from_name(name):
    return df[df['name']==name].index.tolist()[0]


df = pd.read_csv('anime.csv')
dfx = pd.read_csv('clusters.csv')
dfx['name'] = dfx['name'].astype(str)
names = list(df.name.values)
scaler = StandardScaler()
df["members"] = df["members"].astype(float)
df["rating"] = df["rating"].astype(float)
df["rating"].fillna(df["rating"].mean(),inplace = True)
attributes = pd.concat([df["genre"].str.get_dummies(sep=","),pd.get_dummies(df[["type"]]),df[["rating"]],df[["members"]]],axis=1)
attributes = scaler.fit_transform(attributes)
temp = attributes
n = NearestNeighbors(n_neighbors=11).fit(attributes)
d, ix = n.kneighbors(attributes)
n_50 = NearestNeighbors(n_neighbors=51).fit(temp)
d_50, ix_50 = n_50.kneighbors(temp)
all_names_50 = list(df.name.values)
all_names = list(df.name.values)
error1 = []


def from_name_user_rating(x):
    global dfx
    id = get_index_from_name(x)
    vals = [dfx.iloc[id]["0"], dfx.iloc[id]["1"], dfx.iloc[id]["2"], dfx.iloc[id]["3"]]
    max = np.argmax(vals)
    res = []
    for i in range(100):
        column = dfx[str(max)]
        max_value = column.max()
        row = dfx[dfx[str(max)]==max_value]
        value = str(getattr(row, 'name'))
        p = re.compile('    (.*)\n')
        value = p.findall(value)
        res.append(value[0])
        id = row.index
        dfx = dfx.drop(id, axis=0)
    final = []
    i = 0
    count = 0
    while True:
        r = random.random()
        if r > 0.5:
            final.append(res[i])
            count += 1
            if count == 10:
                break
        i += 1
        if i==99:
            j = 0
            while count != 10:
                if res[j] not in final:
                    final.append(res[j])
                    count += 1
                j += 1
            break
    return final, res


def id_from_partial_name(partial):
    flag=0
    y=[]
    for name in all_names:
        if partial.lower() in name.lower():
            y.append(name)
            flag=1            
    if(flag==0):
        y.append("No such anime found")
    return y


def from_name(x):
        id = get_index_from_name(x)
        y = []
        for i in ix[id][1:]:
            y.append(df.iloc[i]["name"])
        return y


def from_id(x):
        y = []
        for x in ix[x][1:]:
            y.append(df.iloc[x]["name"])
        return y


def from_name_50(x):
    id = get_index_from_name(x)
    y = []
    for i in ix_50[id][1:]:
        y.append(df.iloc[i]["name"])
    return y


def top(x):
    global df
    genre = from_name_50(x)
    _, users = from_name_user_rating(x)
    genre = set(genre)
    intersection = genre.intersection(users)
    intersection = list(intersection)
    i = 0
    final = list(intersection)
    genre = list(genre)
    intersection = list(intersection)
    while len(final) < 5:
        if genre[i] not in intersection:
            final.append(genre[i])
        i = i + 1
    return final[:5]    


@app.route('/recommendBN', methods=['GET', 'POST'])


def get_name():
    if error1:
        error1.pop()
    if request.method =='POST':
        byName = request.form.get("name")
        byId = request.form.get("ID")
        if byName in df['name'].values:
            if(byName!=""):
                A, b = from_name_user_rating(byName)
                return render_template('result.HTML', result=from_name(byName), result2=A, result3=top(byName))
            return render_template('result.HTML', result=from_id(int(byId)))
        else:
            error1.append('No such anime found')
            return redirect(url_for('index'))      
    return '''<form method='POST'>
                Byname:<input type="text" id="name" name="name"><br>
                <input type="submit" value="Submit"><br>
              </form>
              <form method='POST'>
                ByID:<input type="text" id="ID" name="ID"><br>
                <input type="submit" value="Submit"><br>
              </form>'''


@app.route('/', methods=['GET', 'POST'])


def index():
    if request.method =='POST':
        part = request.form.get("part")
        return render_template('./index.HTML', result=id_from_partial_name(part)) 
    return render_template('./index.HTML', result2 = error1)


@app.errorhandler(404)


def page_not_found(e):
    return render_template('404.HTML'), 404
# app.run(debug=False, port=5000)
