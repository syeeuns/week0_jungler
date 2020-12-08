from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('@localhost', 27017)
db = client.dbjungletest

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
