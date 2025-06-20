#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, session, request
from flask_migrate import Migrate

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# Clear session (resets page views)
@app.route('/clear')
def clear_session():
    session['page_views'] = 0
    return {'message': '200: Successfully cleared session data.'}, 200

# List all articles
@app.route('/articles')
def index_articles():
    articles = Article.query.all()
    article_list = [{
        'id': article.id,
        'title': article.title,
        'author': article.author,
        'content': article.content,
        'date': str(article.date)
    } for article in articles]

    return jsonify(article_list), 200

# Show a single article with session tracking
@app.route('/articles/<int:id>')
def show_article(id):
    # Initialize or increment page views
    session["page_views"] = session.get("page_views", 0) + 1

    if session['page_views'] <= 3:
        article = Article.query.get_or_404(id)
        words = article.content.split()
        minutes_to_read = max(1, len(words) // 200)

        response = make_response(jsonify({
            'id': article.id,
            'title': article.title,
            'author': article.author,
            'content': article.content,
            'preview': article.content[:100],
            'minutes_to_read': minutes_to_read,
            'date': str(article.date),
            'session': {
                'page_views': session['page_views'],
            },
            'cookies': [{cookie: request.cookies[cookie]} for cookie in request.cookies],
        }), 200)

        response.set_cookie('mouse', 'Cookie')
        return response

    else:
        return jsonify({'message': 'Maximum pageview limit reached'}), 401

if __name__ == '__main__':
    app.run(port=5555)
