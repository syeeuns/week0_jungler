from flask import Flask, render_template, jsonify, request, redirect, url_for
from pymongo import MongoClient
import jwt
import json
from functools import wraps


app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbjungler

# 토큰 생성에 사용될 Secret Key를 flask 환경 변수에 등록
app.config.update(
    DEBUG=True,
    JWT_TOKEN_LOCATION="cookies",
    JWT_SECRET_KEY="jungler-secretKey",
    JWT_ACCESS_COOKIE_PATH="/api/",
    JWT_REFRESH_COOKIE_PATH="/token/refresh",
)

# JWT 확장 모듈을 flask 어플리케이션에 등록
# jwt = JWTManager(app)


@app.route("/")
def test_test():
    # if cookie 존재 > redirect
    if (request.cookies.get('token')):
        return redirect(url_for('home'))

    return render_template('login.html')

# 로그인


@app.route("/login", methods=['POST'])
def login():
    # 클라이언트에서 받은거
    input_data = request.get_json()
    user_id_receive = input_data['id']
    user_pw_receive = input_data['password']

    # DB에서 찾아온거
    userinfo = db.users.find_one({'ID': user_id_receive})
    if (userinfo):
        admin_id = userinfo['ID']
        admin_pw = userinfo['password']
    else:
        return jsonify({"result": "empty", "message": "존재하지 않는 아이디입니다."})

    json_user = {
        "id": user_id_receive,
        "password": user_pw_receive
    }

    if (user_id_receive == admin_id and user_pw_receive == admin_pw):
        encoded = jwt.encode(json_user, "secret_key", algorithm="HS256")
        print(encoded)
        decoded = jwt.decode(encoded, "secret_key", algorithm="HS256")

        print(decoded)
        resp = jsonify({'login': True})
        resp.set_cookie('token', encoded, path='/', httponly=True)
        return resp
    # # 아이디, 비밀번호가 일치하지 않는 경우
    else:
        return jsonify(result="fail")

# 로그아웃


@ app.route('/logout')
def logout():
    if (request.cookies.get('token')):
        resp = jsonify({'result': 'success'})
        # 바로 삭제되는 쿠키를 덮어씌움
        resp.set_cookie('token', '', expires=0)
        return resp

# 회원가입


@ app.route('/register', methods=['POST'])
def registerId():
    # 1. 클라이언트로부터 데이터를 받기
    id_receive = request.form['id_give']  # 클라이언트로부터 url을 받는 부분
    password_receive = request.form['password_give']  # 클라이언트로부터 comment를 받는 부분
    information = {'ID': id_receive, 'password': password_receive}
    # 3. mongoDB에 데이터를 넣기
    db.users.insert_one(information)
    return jsonify({'result': 'success'})

# 데코레이터


def token_required(f):
    @ wraps(f)
    def decorated(*args, **kwargs):
        # 토큰 가져오기
        token = request.cookies.get('token')
        if not token:
            return jsonify({'message': '토큰이 없습니다'}), 403
        try:
            data = jwt.decode(token, "secret_key")
            print(data)
        except:
            return jsonify({'message': '잘못된 토큰입니다'}), 403
        return f(*args, **kwargs)
    return decorated


@ app.route('/home')
@ token_required
def home():
    # cards 디비에 프로필정보 넣기
    cards = list(db.cards.find({}, {'_id': 0}))
    number = len(cards)
    return render_template('index.html', number=number, cards=cards)


@ app.route('/main/search')
@ token_required
def filteredHome():
    # cards 에 search 넣기
    cards = list(db.search.find({}, {'_id': 0}))
    number = len(cards)
    return render_template('index.html', number=number, cards=cards, comment="해당하는 사람은")

# CREATE


@ app.route('/main', methods=['POST'])
def post_info():
    name_receive = request.form['name_give']
    birthday_m_receive = request.form['birthday_m_give']
    birthday_d_receive = request.form['birthday_d_give']
    blood_receive = request.form['blood_give']
    hometown_receive = request.form['hometown_give']
    hometown_detail_receive = request.form['hometown_detail_give']
    mbti_receive = request.form['mbti_give']
    pet_receive = request.form['pet_give']
    pet_detail_receive = request.form['pet_detail_give']
    mood_receive = request.form['mood_give']
    hello_receive = request.form['hello_give']
    user = {
        'name': name_receive,
        'birthday_m': birthday_m_receive,
        'birthday_d': birthday_d_receive,
        'blood': blood_receive,
        'hometown': hometown_receive,
        'hometown_detail': hometown_detail_receive,
        'mbti': mbti_receive,
        'pet': pet_receive,
        'pet_detail': pet_detail_receive,
        'mood': mood_receive,
        'hello': hello_receive
    }
    db.cards.insert_one(user)
    return jsonify({'result': 'success'})


# READ
@ app.route('/main', methods=['GET'])
def read_info():
    result = list(db.cards.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'users': result})


# DELETE
@ app.route('/main/delete', methods=['POST'])  # deleteArticle
def delete_info():
    name_receive = request.form['name_give']
    db.cards.delete_one({'name': name_receive})
    return jsonify({'result': 'success'})

# READ by Filter


@ app.route('/main/search', methods=['POST'])
def search_info():
    db.search.drop()
    birthday_m_receive = request.form.getlist('birthday_m_array[]')
    blood_receive = request.form.getlist('blood_array[]')
    hometown_receive = request.form.getlist('hometown_array[]')
    mbti_receive = request.form.getlist('mbti_array[]')
    pet_receive = request.form.getlist('pet_array[]')
    if birthday_m_receive == []:
        birthday_m_filter = list(db.cards.find({}, {'_id': 0}))
    else:
        birthday_m_filter = list(db.cards.find(
            {'birthday_m': {'$in': birthday_m_receive}}, {'_id': 0}))
    for one in birthday_m_filter:
        db.search.insert_one(one)
    search_filter(blood_receive, 'blood')
    search_filter(hometown_receive, 'hometown')
    search_filter(mbti_receive, 'mbti')
    search_filter(pet_receive, 'pet')
    return jsonify({'result': 'success'})


def search_filter(tags, category):
    if tags:
        filter_result = list(db.search.find(
            {category: {'$in': tags}}, {'_id': 0}))
        db.search.drop()
        for one in filter_result:
            db.search.insert_one(one)


@ app.route('/main/search', methods=['GET'])
def search_read():
    return


if __name__ == '__main__':
    app.run(debug=True)
