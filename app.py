from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client.dbjungler


@app.route('/')
def home():
    # cards에 users 넣기
    cards = list(db.users.find({}, {'_id': 0}))
    number = len(cards)
    return render_template('index.html', number=number, cards=cards)


@app.route('/main/search')
def filteredHome():
    # cards 에 search 넣기
    cards = list(db.search.find({}, {'_id': 0}))
    number = len(cards)
    return render_template('index.html', number=number, cards=cards)
# CREATE


@app.route('/main', methods=['POST'])
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
    db.users.insert_one(user)
    return jsonify({'result': 'success'})
# READ


@app.route('/main', methods=['GET'])
def read_info():
    result = list(db.users.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'users': result})
# DELETE


@app.route('/main/delete', methods=['POST'])  # deleteArticle
def delete_info():
    name_receive = request.form['name_give']
    db.users.delete_one({'name': name_receive})
    return jsonify({'result': 'success'})


@app.route('/main/search', methods=['POST'])
def search_info():
    db.search.drop()
    birthday_m_receive = request.form.getlist('birthday_m_array[]')
    blood_receive = request.form.getlist('blood_array[]')
    hometown_receive = request.form.getlist('hometown_array[]')
    mbti_receive = request.form.getlist('mbti_array[]')
    pet_receive = request.form.getlist('pet_array[]')
    if birthday_m_receive == []:
        birthday_m_filter = list(db.users.find({}, {'_id': 0}))
    else:
        birthday_m_filter = list(db.users.find(
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


@app.route('/main/search', methods=['GET'])
def search_read():
    return


if __name__ == '__main__':
    app.run(debug=True)
# #UDATE
# @app.route('/memo/update', methods=['POST'])  #updateArticle
# def update_articles():
#     oldTitle_receive = request.form['oldTitle_give']
#     title_receive = request.form['title_give']
#     comment_receive = request.form['comment_give']
#     db.articles.update_one({'title': oldTitle_receive}, {'$set': {'title':title_receive, 'comment': comment_receive}})
#     return jsonify({'result': 'success'})
