from pymongo import MongoClient
import jwt, certifi, requests, datetime, hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

ca = certifi.where()
client = MongoClient('mongodb+srv://hyunjin9603:1234@cluster0.lnp9zul.mongodb.net/?retryWrites=true&w=majority',tlsCAFile=ca)
db = client.dbsparta

@app.route('/')
def home():
   return render_template('index.html')

@app.route("/coding", methods=["POST"])
def coding_post():
    coding_receive = request.form["coding_give"]
    meaning_receive = request.form["meaning_give"]

    count = db.coding.count_documents({})
    num = count + 1

    doc = {
        'num': num,
        'coding': coding_receive,
        'meaning': meaning_receive,
        'done': 0
    }

    db.coding.insert_one(doc)
    return jsonify({'msg':'등록 완료!'})

@app.route("/coding/restore", methods=["POST"])
def coding_restore():
    num_receive = request.form["num_give"]
    db.coding.update_one({'num': int(num_receive)}, {'$set': {'done': 0}})
    return jsonify({'msg': '북마크 취소!'})

@app.route("/coding/bookmark", methods=["POST"])
def coding_bookmark():
    num_receive = request.form["num_give"]
    db.coding.update_one({'num': int(num_receive)}, {'$set': {'done': 1}})
    return jsonify({'msg': '북마크 완료!'})

@app.route("/coding", methods=["GET"])
def coding_get():
    coding_list = list(db.coding.find({},{'_id':False}))
    return jsonify({'coding':coding_list})



if __name__ == '__main__':
   app.run('0.0.0.0', port=4000, debug=True)