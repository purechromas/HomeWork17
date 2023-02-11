from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from movies_data import data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)

with app.app_context():
    class Movie(db.Model):
        __tablename__ = 'movie'
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(255))
        description = db.Column(db.String(255))
        trailer = db.Column(db.String(255))
        year = db.Column(db.Integer)
        rating = db.Column(db.Float)
        genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
        genre = db.relationship("Genre")
        director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
        director = db.relationship("Director")


    class Director(db.Model):
        __tablename__ = 'director'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(255))


    class Genre(db.Model):
        __tablename__ = 'genre'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(255))


    class MovieSchema(Schema):
        id = fields.Int(dump_only=True)
        title = fields.Str()
        description = fields.Str()
        trailer = fields.Str()
        year = fields.Int()
        rating = fields.Float()
        genre_id = fields.Int()
        director_id = fields.Int()


    class DirectorSchema(Schema):
        id = fields.Int(dump_only=True)
        name = fields.Str()


    class GenreSchema(Schema):
        id = fields.Int(dump_only=True)
        name = fields.Str()


    db.create_all()

    for movie in data["movies"]:
        m = Movie(
            id=movie["pk"],
            title=movie["title"],
            description=movie["description"],
            trailer=movie["trailer"],
            year=movie["year"],
            rating=movie["rating"],
            genre_id=movie["genre_id"],
            director_id=movie["director_id"],
        )
        db.session.add(m)
        db.session.commit()

    for director in data["directors"]:
        d = Director(
            id=director["pk"],
            name=director["name"],
        )
        db.session.add(d)
        db.session.commit()

    for genre in data["genres"]:
        d = Genre(
            id=genre["pk"],
            name=genre["name"],
        )
        db.session.add(d)
        db.session.commit()

    print(Movie.query.filter_by(genre_id=7).all())

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

ns_movies = api.namespace('movies')
ns_directors = api.namespace('directors')
ns_genres = api.namespace('genres')


@ns_movies.route('/')
class MoviesView(Resource):
    def get(self):
        data_director_id = request.args.get('director_id')
        data_genre_id = request.args.get('genre_id')
        if data_director_id and data_genre_id:
            ddidgimix = Movie.query.filter_by(director_id=data_director_id, genre_id=data_genre_id).all()
            return movies_schema.dump(ddidgimix), 200
        elif data_director_id:
            ddi = Movie.query.filter_by(director_id=data_director_id).all()
            return movies_schema.dump(ddi), 200
        elif data_genre_id:
            dgi = Movie.query.filter_by(genre_id=data_genre_id.all()
            return movies_schema.dump(dgi), 200
        else:
            movies = Movie.query.all()
            return movies_schema.dump(movies), 200


@ns_movies.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid):
        movie = db.session.get(Movie, mid)
        return movie_schema.dump(movie), 200


@ns_directors.route('/')
class DirectorView(Resource):
    def post(self):
        new_director = request.json
        Director(**new_director)
        return "", 201


@ns_directors.route('/<int:did>')
class DirectorView(Resource):
    def put(self, did):
        director_data = Director.query.get(did)
        new_director_data = request.json
        director_data.name = new_director_data['name']

        db.session.add(director_data)
        db.session.commit()

        return "", 204

    def delete(self, did):
        db.session.query(Director).filter_by(id=did).delete()
        db.session.commit()

        return "", 204


@ns_genres.route('/')
class GenresView(Resource):
    def post(self):
        new_genre = request.json
        Genre(**new_genre)
        return "", 201


@ns_genres.route('/<int:gid>')
class GenreView(Resource):
    def put(self, gid):
        genre_data = db.session.get(Genre, gid)
        new_genre_data = request.json
        genre_data.name = new_genre_data['name']

        db.session.add(genre_data)
        db.session.commit()

        return "", 204

    def delete(self, gid):
        db.session.query(Genre).filter_by(id=gid).delete()
        db.session.commit()

        return "", 204


if __name__ == '__main__':
    app.run()
