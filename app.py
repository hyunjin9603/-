from pymongo import MongoClient
import jwt, certifi, hashlib, datetime, requests

from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import certifi

app = Flask(__name__)
app.config["TEMPLATES_AUTO RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

ca = certifi.where()
client = MongoClient("mongodb+srv://test:sparta@cluster0.d9pmfhg.mongodb.net/Cluster0?retryWrites=true&w=majority", tlsCAFile=ca)

db = client.dbsparta

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 유저 정보 전달하기
        words = list(db.words.find({}, {'_id': False}))
        user_info = db.users.find_one({"username": payload["id"]},{'_id':False})['username']
        return render_template('index.html', user_info=user_info,words=words)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))




@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('/static/templates/login.html', msg=msg)


@app.route('/word/login', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 회원가입
@app.route('/word/join', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "profile_info": ""  # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success', 'msg': '회원가입을 축하합니다!'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    # ID 중복확인
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/words', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 포스팅하기
        user_info = db.users.find_one({"username": payload["id"]})
        word_receive = request.form["word_give"]
        meaning_receive = request.form["meaning_give"]

        commend_list = list(db.save.find({}, {'_id': False}))
        count = len(commend_list) + 1

        doc = {
            "word": word_receive,
            "meaning": meaning_receive,
            "num": count
        }
        db.words.insert_one(doc)
        return jsonify({"result": "success", 'msg': '등록 완료'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect("/")

@app.route("/words/delete", methods=["POST"])
def delete_word():
    word_receive = request.form['word_give']
    db.words.delete_one({"word": word_receive})
    return jsonify({'msg': f'word "{word_receive}"삭제완료!'})

@app.route("/words", methods=['GET'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]}, {'_id':False})
        username = user_info['username']
        # 포스팅 목록 받아오기
        words = list(db.words.find({}))
        for word in words:
            word['_id'] = str(word['_id'])
            word["bookmark_by_me"] = bool(db.likes.find_one({'word_id': word['_id'], "username": payload['id']}))

        print(words)
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", 'words': words})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route('/update_bookmark', methods=['POST'])
def update_bookmark():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        # 좋아요 수 변경
        user_info = db.users.find_one({"username": payload["id"]})
        word_id_receive = request.form["word_id_give"]
        action_receive = request.form["action_give"]
        doc = {
            "word_id": word_id_receive,
            "username": user_info["username"]
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)

        return jsonify({"result": "success", 'msg': 'updated'})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

if __name__ == '__main__':
    app.run('0.0.0.0', port=4000, debug=True)

app.route("/bookmark", methods=['GET'])
def show_bookmark():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        words = list(db.words.find({}))
        for word in words:
            word['_id'] = str(word['_id'])
            word["bookmark_by_me"] = bool(db.likes.find_one({'word_id': word['_id'], "username": payload['id']}))

        print(words)
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", 'words': words})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=4000, debug=True)

