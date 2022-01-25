from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, ForeignKey, true
from flask_restful import Api, Resource
from flask_cors import CORS
from sqlalchemy.orm import backref
from datetime import date
import os
import jwt
from functools import wraps

pv_key = 'NTNv7j0TuYARvmNMmWXo6fKvM4o6nv/aUi9ryX38ZH+L1bkrnD1ObOQ8JAUmHCBq7Iy7otZcyAagBLHVKvvYaIpmMuxmARQ97jUVG16Jkpkp1wXOPsrF9zwew6TpczyHkHgX5EuLg2MeBuiT/qJACs1J0apruOOJCg/gOtkjB4c='
# adminToken: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjIiLCJhZG1pbiI6dHJ1ZSwiaWF0IjoxNjQzMTAzMDQ4LCJleHAiOjE2NDkxMDYyODB9.8uSDheikn1lfG_WhtwYmEGZ6NeWvAZVXlqdPCdd-O2w

# userToken: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjEiLCJhZG1pbiI6ZmFsc2UsImlhdCI6MTY0MzEwMzA0OCwiZXhwIjoxNjQ5MTA2MjgwfQ.Hvjg4kk6LefEsjpX2MF4d0mP6o3uRw4FRy1L_g-_rfI



app = Flask(__name__)
CORS(app)

cors = CORS(app, resource={
    r"/*" : {
        "origins" : "*"
    }
})
api = Api(app)

app.config['SECRET_KEY'] = pv_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.curdir , 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    usernmame = Column(String(100), unique=True)
    password = Column(String(100), nullable=False)
    role = Column(Integer, nullable=False)

class Movie(db.Model):
    __tablename__ = 'Movie'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(1000))
    rating = Column(Float)

class Comment(db.Model):
    __tablename__ = 'Comment'
    id = Column(Integer, primary_key=True)
    comment = Column(String(1000), nullable=False)
    approved = Column(Boolean, nullable=False)
    createdAt = Column(DateTime)
    userID = Column(Integer, ForeignKey('User.id'))
    user = db.relationship("User", backref=backref("User", uselist=False))
    movieID = Column(Integer, ForeignKey('Movie.id'))
    movie = db.relationship("Movie", backref=backref("Movie", uselist=False))

class Rate(db.Model):
    __tablename__ = 'Rate'
    id = Column(Integer, primary_key=True)
    userID = Column(Integer, nullable=False)
    rating = Column(Float)
    movieID = Column(Integer, nullable=False)

class movieApi(Resource):
    def get(self):
        print(self)
        movies = []
        try:
            movieInDB = Movie.query.all()
        except Exception as ex:
            resp = make_response(jsonify(
            {
                'message': 'There is an internal issue.'
            }), 500)
            return resp
        
        for item in movieInDB:
            movies.append({
              'id': item.id ,
              'name': item.name,
              'description': item.description,
              'rating': item.rating
            })
        resp = make_response(jsonify(
            {
                'movies': movies
            }
        ), 200)
        resp.headers['Content-Type'] = 'application/json'
        return resp

class CommentApi(Resource):
    def get(self):
        id = request.args['movie']
        if not id:
            resp = make_response(jsonify(
            {
                'message': 'Bad request.'
            }), 400)
            return resp
        comments = []
        try:
            movie = Movie.query.get(id)
            if movie == None:
                resp = make_response(jsonify({'message': 'Not found.'}), 404)
                return resp
            commentsInDB = Comment.query.join(User, Comment.userID == User.id)\
            .add_columns(User.usernmame, Comment.id, Comment.comment, Comment.movieID, Comment.approved)\
            .filter(Comment.movieID == id)
            
            
        except Exception as ex:
            resp = make_response(jsonify(
            {
                'message': 'There is an internal issue.'
            }), 500)
            return resp
        for item in commentsInDB:
            if item.approved:
                comments.append({
                "id": item.id,
                "author": item.usernmame,
                "body": item.comment
                })
                
            
        resp = make_response(jsonify(
            {
                'movie': movie.name,
                'comments': comments
            }
        ), 200)
        resp.headers['Content-Type'] = 'application/json'
        return resp

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            token = token.split(' ')[1]
        # return 401 if token is not passed
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
  
        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, pv_key, algorithms=["HS256"])
            current_user = User.query\
                .filter_by(id = data['id'])\
                .first()
        except:
            return jsonify({'message' : 'Token is invalid !!'}), 401
        # returns the current logged in users contex to the routes
        return  f(current_user, *args, **kwargs)
  
    return decorated

api.add_resource(movieApi, '/movies')
api.add_resource(CommentApi, '/comments')

@app.route('/movie/<movie_id>')
def getMovie(movie_id):
    id = movie_id
    try:
        movie = Movie.query.get(id)
        if movie == None:
            resp = make_response(jsonify({'message': 'Bad request.'}), 400)
            return resp
    except Exception as _:
        resp = make_response(jsonify({'message': 'There is an internal issue.'}), 500)
        return resp

    resp = make_response(jsonify(
            { 
              'id': movie.id ,
              'name': movie.name,
              'description': movie.description,
              'rating': movie.rating
            }
        ), 200)
    return resp

@app.route('/admin/movie', methods=['POST'])
@token_required
def postMovie(current_user):
    if current_user.role != 1:
        resp = make_response(jsonify({'message': 'You dont have access'}), 400)
        return resp
    try:
        newMovie = request.get_json()
        newMovie['name']
        newMovie['description']
    except Exception as ex:
        resp = make_response(jsonify({'message': 'Bad request.'}), 400)
        return resp
    
    if (newMovie == None) or (newMovie['name'] == None) or (newMovie['description'] == None):
        resp = make_response(jsonify({'message': 'Bad request.'}), 400)
        return resp


    newItem = Movie(name=newMovie['name'], description= newMovie['description'], rating=0)
    db.session.add(newItem)
    db.session.commit()
    resp = make_response(jsonify({'message': 'Ok.'}), 204)
    return resp
    
@app.route('/admin/movie/<movie_id>', methods=['PUT'])
@token_required
def changeMovieInfo(current_user,movie_id):
    if current_user.role != 1:
        resp = make_response(jsonify({'message': 'You dont have access'}), 400)
        return resp
    id = movie_id
    try:
        movie = Movie.query.get(id)
        if movie == None:
            resp = make_response(jsonify(
            {
                'message': 'Bad request.'
            }), 400)
            return resp
    except Exception as _:
        resp = make_response(jsonify(
            {
                'message': 'There is an internal issue.'
            }), 500)
        return resp

    try:
        newMovie = request.get_json()
        newMovie['name']
        newMovie['description']
    except Exception as ex:
        resp = make_response(jsonify({'message': 'Bad request.'}), 400)
        return resp
    
    movie.name = newMovie['name']
    movie.description = newMovie['description']
    db.session.commit()
    
    resp = make_response(jsonify({ 'message': 'ok' ,}), 204)
    return resp

@app.route('/admin/movie/<movie_id>', methods=['DELETE'])

def deleteMovie(current_user, movie_id):
    if current_user.role != 1:
        resp = make_response(jsonify({'message': 'You dont have access'}), 400)
        return resp
    id = movie_id
    try:
        if not id.isnumeric():
            resp = make_response(jsonify({'message': 'Bad request.'}), 400)
            return resp
        movie = Movie.query.get(id)
        if movie == None:
            resp = make_response(jsonify({'message': 'Bad request.'}), 400)
            return resp
    except Exception as _:
        resp = make_response(jsonify(
            {
                'message': 'There is an internal issue.'
            }), 500)
        return resp
    Movie.query.filter(Movie.id == id).delete()
    db.session.commit()
    
    resp = make_response(jsonify({ 'message': 'ok' ,}), 204)
    return resp

@app.route('/admin/comment/<comment_id>', methods=['PUT'])
@token_required
def approvedComment(current_user ,comment_id):
    if current_user.role != 1:
        resp = make_response(jsonify({'message': 'You dont have access'}), 400)
        return resp
    id = comment_id
    try:
        comment = Comment.query.get(id)
        if comment == None:
            resp = make_response(jsonify({'message': 'Bad request.'}), 400)
            return resp
    except Exception as _:
        resp = make_response(jsonify({'message': 'There is an internal issue.' }), 500)
        return resp

    try:
        newData = request.get_json()
        newData['approved']
        if type(newData['approved']) != type(True):
            resp = make_response(jsonify({'message': 'Bad request.'}), 400)
            return resp     
    except Exception as ex:
        resp = make_response(jsonify({'message': 'Bad request.'}), 400)
        return resp
    
    comment.approved = newData['approved']
    db.session.commit()
    
    resp = make_response(jsonify({ 'message': 'ok' ,}), 204)
    return resp

@app.route('/admin/comment/<comment_id>', methods=['DELETE'])
@token_required
def deleteComment(current_user ,comment_id):
    if current_user.role != 1:
        resp = make_response(jsonify({'message': 'You dont have access'}), 400)
        return resp
    id = comment_id
    try:
        if not id.isnumeric():
            resp = make_response(jsonify({'message': 'Bad request.'}), 400)
            return resp
        comment = Comment.query.get(id)
        if comment == None:
            resp = make_response(jsonify({'message': 'Bad request.'}), 400)
            return resp
    except Exception as _:
        resp = make_response(jsonify(
            {
                'message': 'There is an internal issue.'
            }), 500)
        return resp
    Comment.query.filter(Comment.id == id).delete()
    db.session.commit()
    
    resp = make_response(jsonify({ 'message': 'ok' ,}), 204)
    return resp

@app.route('/user/vote', methods=['POST'])
@token_required
def voteMovie(current_user):
    if current_user.role == 1:
        resp = make_response(jsonify({'message': 'You dont have access'}), 400)
        return resp
    try:
        vote = request.get_json()
        vote['movie_id']
        vote['vote']
        if vote['vote'] > 1 and vote['vote'] < 0:
            resp = make_response(jsonify({'message': 'Bad request.'}), 400)
            return resp

    except Exception as ex:
        resp = make_response(jsonify({'message': 'Bad request.'}), 400)
        return resp
    

    
    movie = Movie.query.get(vote['movie_id'])
    if movie == None:
        resp = make_response(jsonify({'message': 'Not found.'}), 400)
        return resp
    
    try:
        voteInDB = Rate.query.filter_by(movieID = vote['movie_id'])
    except Exception as ex:
        resp = make_response(jsonify(
        {'message': 'There is an internal issue.'}), 500)
        return resp

    if (vote == None) or (vote['movie_id'] == None) or (vote['vote'] == None):
        resp = make_response(jsonify({'message': 'Bad request.'}), 400)
        return resp

    
    allRates = 0
    num = 0
    for item in voteInDB:
        print(item.rating)
        allRates += item.rating
        num += 1
    avgRate = (allRates + vote['vote']) / (num + 1)
    print(avgRate)
    movie.rating = avgRate

   


    newItem = Rate(movieID=vote['movie_id'], rating= vote['vote'], userID=current_user.id)
    db.session.add(newItem)
    db.session.commit()
    return make_response(jsonify({'message': 'OK'}), 204)

@app.route('/user/comment', methods=['POST'])
@token_required
def commentMovie(current_user):
    if current_user.role == 1:
        resp = make_response(jsonify({'message': 'You dont have access'}), 400)
        return resp
    try:
        comment = request.get_json()
        comment['movie_id']
        comment['comment_body']
    except Exception as ex:
        resp = make_response(jsonify({'message': 'Bad request.'}), 400)
        return resp
    
    if (comment == None) or (comment['movie_id'] == None) or (comment['comment_body'] == None):
        resp = make_response(jsonify({'message': 'Bad request.'}), 400)
        return resp


    newItem = Comment(createdAt = date.today(), approved = False, movieID=comment['movie_id'], comment= comment['comment_body'], userID=current_user.id)
    db.session.add(newItem)
    db.session.commit()
    return make_response(jsonify({'message': 'OK'}), 200)
   