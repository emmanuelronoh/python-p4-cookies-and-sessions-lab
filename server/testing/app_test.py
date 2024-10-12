import pytest
import flask
from app import app, db, Article, User

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    
    with app.app_context():
        db.create_all()  
        test_user = User(name='Test User')
        db.session.add(test_user)
        db.session.commit()
        yield app.test_client()
        db.drop_all()

@pytest.fixture
def setup_articles(test_client):
    with app.app_context():
        user_id = User.query.first().id  
        articles = [
            Article(author='Author 1', title='Title 1', content='Content 1', preview='Preview 1', minutes_to_read=5, user_id=user_id),
            Article(author='Author 2', title='Title 2', content='Content 2', preview='Preview 2', minutes_to_read=10, user_id=user_id),
            Article(author='Author 3', title='Title 3', content='Content 3', preview='Preview 3', minutes_to_read=15, user_id=user_id)
        ]
        db.session.add_all(articles)
        db.session.commit()

def test_show_articles_route(test_client, setup_articles):
    response = test_client.get('/articles/1')
    response_json = response.get_json()
    
    assert response_json.get('author') is not None
    assert response_json.get('title') is not None
    assert response_json.get('content') is not None
    assert response_json.get('preview') is not None
    assert response_json.get('minutes_to_read') is not None
    assert response_json.get('date') is not None

def test_increments_session_page_views(test_client):
    with test_client as client:
        client.post('/clear')  

        # View first article
        response = client.get('/articles/1')
        assert response.status_code == 200
        assert flask.session.get('page_views') == 1

        # View second article
        response = client.get('/articles/2')
        assert response.status_code == 200
        assert flask.session.get('page_views') == 2

        # View third article
        response = client.get('/articles/3')
        assert response.status_code == 200
        assert flask.session.get('page_views') == 3

        # Attempt to view a fourth article (should trigger the limit)
        response = client.get('/articles/1')  # This should trigger the limit check
        assert response.status_code == 401
        assert response.get_json().get('message') == 'Maximum pageview limit reached'

def test_limits_three_articles(test_client, setup_articles):
    with test_client as client:
        client.post('/clear')  

        response = client.get('/articles/1')
        assert response.status_code == 200
        
        response = client.get('/articles/2')
        assert response.status_code == 200

        response = client.get('/articles/3')
        assert response.status_code == 200

        response = client.get('/articles/1')  # This should trigger the limit check
        assert response.status_code == 401
        assert response.get_json().get('message') == 'Maximum pageview limit reached'
