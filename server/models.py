from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin

# Define naming convention for foreign keys
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# Initialize the SQLAlchemy object
db = SQLAlchemy(metadata=metadata)

class Article(db.Model, SerializerMixin):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, nullable=False)  # Not nullable
    title = db.Column(db.String, nullable=False)   # Not nullable
    content = db.Column(db.Text, nullable=False)    # Changed to Text for larger content
    preview = db.Column(db.String)
    minutes_to_read = db.Column(db.Integer)
    date = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key

    def to_dict(self):
        return {
            'id': self.id,
            'author': self.author,
            'title': self.title,
            'content': self.content,
            'preview': self.preview,
            'minutes_to_read': self.minutes_to_read,
            'date': self.date.isoformat() if self.date else None,
            'user_id': self.user_id  # Include user_id for clarity
        }

    def __repr__(self):
        return f'<Article {self.id} by {self.author}>'

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)  # Not nullable

    articles = db.relationship('Article', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'articles': [article.to_dict() for article in self.articles]
        }

    def __repr__(self):
        return f'<User {self.name}, ID {self.id}>'
