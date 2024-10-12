#!/usr/bin/env python3

from flask import Flask, jsonify, session, request
from flask_migrate import Migrate
from models import db, Article, User  # Make sure to import User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/clear', methods=['POST'])
def clear_session():
    """Clear all session data."""
    session.clear()  # Clear all session data
    return {'message': '200: Successfully cleared session data.'}, 200

@app.route('/articles', methods=['GET', 'POST'])
def index_articles():
    """Return a list of articles or create a new article."""
    if request.method == 'POST':
        data = request.get_json()
        
        # Ensure user_id is provided for article creation
        user_id = data.get('user_id')  # Expect user_id to be part of the request
        if not user_id:
            return jsonify({'message': 'User ID is required.'}), 400
        
        new_article = Article(
            author=data.get('author'),
            title=data.get('title'),
            content=data.get('content'),
            preview=data.get('preview'),
            minutes_to_read=data.get('minutes_to_read'),
            user_id=user_id  # Set the user_id for the article
        )
        
        db.session.add(new_article)
        db.session.commit()
        return jsonify(new_article.to_dict()), 201

    articles = Article.query.all()
    return jsonify([article.to_dict() for article in articles]), 200

@app.route('/articles/<int:id>', methods=['GET'])
def show_article(id):
    """Show a single article by ID."""
    if 'page_views' not in session:
        session['page_views'] = 0
    session['page_views'] += 1

    if session['page_views'] > 3:
        return jsonify({'message': 'Maximum pageview limit reached'}), 401

    article = Article.query.get(id)
    if not article:
        return jsonify({'message': 'Article not found'}), 404

    return jsonify(article.to_dict()), 200

if __name__ == '__main__':
    app.run(port=5555)
