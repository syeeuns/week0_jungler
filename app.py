from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from flask_jwt_extended import *


app = Flask(__name__)

client = MongoClient('mongodb://test:test@localhost', 27017)
db = client.dbjungletest

# 토큰 생성에 사용될 Secret Key를 flask 환경 변수에 등록
app.config.update(
			DEBUG = True,
			JWT_SECRET_KEY = "I'M GEM"
		)

# JWT 확장 모듈을 flask 어플리케이션에 등록
jwt = JWTManager(app)

@app.route("/")
def test_test():
	return render_template('login.html')

# 로그인 API 영역

admin_id = "1234"
admin_pw = "qwer"

@app.route("/login", methods=['POST'])
def login_proc():
	
	# 클라이언트로부터 요청된 값
	input_data = request.get_json()
	user_id = input_data['id']
	user_pw = input_data['password']

	# 아이디, 비밀번호가 일치하는 경우
	if (user_id == admin_id and
		user_pw == admin_pw):
		return jsonify(
			result = "success",
			# 검증된 경우, access 토큰 반환
			access_token = create_access_token(identity = user_id,
											expires_delta = False)
		)
		

	# 아이디, 비밀번호가 일치하지 않는 경우
	else:
		return jsonify(
			result = "fail"
		)

@app.route('/check_login', methods=['POST'])
def check_login():
    	return render_template('index.html')

#################################################
# 회원 전용 API 영역
@app.route('/user_only', methods=["GET"])
@jwt_required
def user_only():
	cur_user = get_jwt_identity()
	if cur_user is None:
		return "User Only!"
	else:
		return "Hi!," + cur_user

@app.route('/')
def home():
    return render_template('index.html')

#CREATE
@app.route('/memo', methods=['POST']) #postArticle
def post_article():
    title_receive = request.form['title_give']
    comment_receive = request.form['comment_give']
    article = {'title': title_receive, 'comment': comment_receive}
    db.articles.insert_one(article)

    return jsonify({'result': 'success'})

#READ
@app.route('/memo', methods=['GET'])  #showArticles
def read_articles():
    result = list(db.articles.find({}, {'_id': 0}))

    return jsonify({'result': 'success', 'articles': result})

#UDATE
@app.route('/memo/update', methods=['POST'])  #updateArticle
def update_articles():
    oldTitle_receive = request.form['oldTitle_give']
    title_receive = request.form['title_give']
    comment_receive = request.form['comment_give']
    db.articles.update_one({'title': oldTitle_receive}, {'$set': {'title':title_receive, 'comment': comment_receive}})

    return jsonify({'result': 'success'})

# DELETE
@app.route('/memo/delete', methods=['POST'])  #deleteArticle
def delete_articles():
    title_receive = request.form['title_give']
    db.articles.delete_one({'title': title_receive})
    return jsonify({'result': 'success'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
