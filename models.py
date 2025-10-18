from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 👤 User model
class User(db.Model):
    """
    Represents a user in the system.

    Attributes:
        id (int): Primary key.
        name (str): Unique name of the user.
        movies (list[Movie]): List of movies associated with the user.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    # Relationship: one user has many movies
    movies = db.relationship("Movie", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.name}>"

# 🎬 Movie model
class Movie(db.Model):
    """
    Represents a movie entry linked to a user.

    Attributes:
        id (int): Primary key.
        name (str): Title of the movie.
        director (str): Director's name.
        year (int): Release year.
        poster_url (str): URL to the movie poster.
        user_id (int): Foreign key linking to the owning user.
    """
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    director = db.Column(db.String(100))
    year = db.Column(db.Integer)
    poster_url = db.Column(db.String(300))

    # Foreign key: link to User
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Movie {self.name} ({self.year})>"

