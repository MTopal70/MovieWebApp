from models import db, User, Movie
from sqlalchemy.exc import SQLAlchemyError


class DataManager:
    # Create a new user
    def create_user(self, name):
        """Create a new user if the name is valid; rollback on failure."""
        if not name or name.strip() == "":
            raise ValueError("User name cannot be empty or whitespace.")

        try:
            new_user = User(name=name.strip())
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    # Get all users
    def get_users(self):
        return User.query.order_by(User.name).all()

# Get one user
    def get_user(self, user_id):
        return User.query.get(user_id)

    # Get all movies for a specific user
    def get_movies(self, user_id):
        return Movie.query.filter_by(user_id=user_id).order_by(Movie.name).all()

    # Get a single movie by ID
    def get_movie(self, movie_id):
        return Movie.query.get(movie_id)

    # Add a new movie (expects a Movie object)
    def add_movie(self, movie):
        db.session.add(movie)
        db.session.commit()
        return movie

    # Update a movie's title
    def update_movie(self, movie_id, new_title):
        movie = Movie.query.get(movie_id)
        if movie:
            movie.name = new_title
            db.session.commit()
        return movie

    # Delete a movie
    def delete_movie(self, movie_id):
        movie = Movie.query.get(movie_id)
        if movie:
            db.session.delete(movie)
            db.session.commit()
        return movie

