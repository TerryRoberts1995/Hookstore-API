from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from dotenv import dotenv_values
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import os
config = dotenv_values('.env')
os.environ['DATABASE_URL'] = config['DATABASE_URL']
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:" + os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)
bcrypt = Bcrypt(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password')

user_schema = UserSchema()
multiple_user_schema = UserSchema(many=True)

@app.route('/user/add', methods=['POST'])
def add_user():
    if request.content_type != 'application/json':
        return jsonify("Error: Data must be JSON.")

    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")

    possible_duplicate = db.session.query(User).filter(User.username == username).first()

    if possible_duplicate is not None:
        return jsonify('Error: That username is Taken.')
    
    encrypted_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username, encrypted_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify('New user has been added.')

@app.route('/user/verify', methods=['POST'])
def verify_user():
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be JSON.')

    post_data = request.get_json()
    username = post_data.get('username')
    password = post_data.get('password')

    user = db.session.query(User).filter(User.username == username).first()

    if user is None:
        return jsonify('User NOT verified.')

    if bcrypt.check_password_hash(user.password, password) == False:
        return jsonify('User NOT verified')

    return jsonify('User has been verified.')
    

@app.route('/user/get', methods=['GET'])
def get_users():
    all_users = db.session.query(User).all()
    return jsonify(multiple_user_schema.dump(all_users))

@app.route('/user/get/<id>', methods=['GET'])
def get_user_by_id(id):
    user = db.session.query(User).filter(User.id == id).first()
    return jsonify(user_schema.dump(user))

@app.route('/user/get/username/<username>', methods=['GET'])
def get_user_by_username(username):
    user = db.session.query(User).filter(User.username == username).first()
    return jsonify(user_schema.dump(user))

@app.route('/user/delete', methods=['DELETE'])
def delete_users():
    all_users = db.session.query(User).all()
    for user in all_users:
        db.session.delete(user)
    db.session.commit()
    return jsonify("All users have has been deleted.")

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    author = db.Column(db.String, nullable=False)
    review = db.Column(db.String(144), nullable=True)
    genre = db.Column(db.String, nullable=True)

    def __init__(self, title, author, review, genre):
        self.title = title
        self.author = author
        self.review = review
        self.genre = genre

class BookSchema(ma.Schema):
    class Meta: 
        fields = ("id", "title", "author", "review", "genre")

book_schema = BookSchema()
multiple_book_schema = BookSchema(many=True)

@app.route("/book/add", methods=["POST"])
def add_book():
    if request.content_type != "application/json":
        return jsonify('Error: Data must be JSON.')

    post_data = request.get_json()
    title = post_data.get('title')
    author = post_data.get('author')
    review = post_data.get('review')
    genre = post_data.get('genre')


    if title == None:
        return jsonify("Error: Data must have a 'Title' key.")

    if author == None:
        return jsonify("Error: data must have 'Author' key.")

    new_record = Book(title, author, review, genre)
    db.session.add(new_record)
    db.session.commit()

    return jsonify("You've added a book!")

@app.route("/book/get", methods=["GET"])
def get_books():
    books = db.session.query(Book).all()
    return jsonify(multiple_book_schema.dump(books))

@app.route('/book/get/<id>', methods=['GET'])
def get_book_by_id(id):
    book = db.session.query(Book).filter(Book.id == id).first()
    return jsonify(book_schema.dump(book))

@app.route('/book/delete/<id>', methods=['DELETE'])
def delete_book_by_id(id):
    book = db.session.query(Book).filter(Book.id == id).first()
    db.session.delete(book)
    db.session.commit()
    return jsonify("Book has been deleted.")

@app.route('/book/update/<id>', methods=['PUT'])
def update_book_by_id(id):
    if request.content_type != "application/json":
        return jsonify("Error: Data must be json")

    post_data = request.get_json()
    title = post_data.get('title')
    author = post_data.get('author')
    review = post_data.get('review')
    genre = post_data.get('genre')

    book = db.session.query(Book).filter(Book.id == id).first()

    if title != None:
        book.title = title
    if author != None:
        book.author = author
    if review != None:
        book.review = review
    if genre != None:
        book.genre = genre

    db.session.commit()
    return jsonify("Book Updated Successfully")

if __name__ == "__main__":
    app.run(debug=True)
