from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://jihyeun_moon:wlgus5490@cluster0.1nmoovx.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

@app.route('/')
def home():
    words = list(db.save.find({}, {"_id": False}))
    return render_template('main.html', words=words)

@app.route("/save", methods=["POST"])
def web_save_post():
    term_receive = request.form['term_give']
    mean_receive = request.form['mean_give']
    doc = {
        'term':term_receive,
        'mean':mean_receive,
    }
    db.save.insert_one(doc)
    return jsonify({'msg': '사전 등록 완료'})

@app.route("/save", methods=["GET"])
def web_save_get():
    save_list = list(db.save.find({}, {'_id': False}))
    return jsonify({'save':save_list})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)