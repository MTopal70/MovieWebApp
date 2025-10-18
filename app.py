import flask
from flask import Flask, request, redirect, url_for, render_template, flash
from sqlalchemy.exc import SQLAlchemyError

from models import db, Movie, User
from data_manager import DataManager
from config import OMDB_API_KEY, SECRET_KEY
from sqlalchemy.exc import SQLAlchemyError
import requests
import os


# Initialize Flask app
app = Flask(__name__)

# Configure SQLite DB path and settings
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "data", "moviweb.sqlite")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = SECRET_KEY

# Initialize SQLAlchemy with Flask app
db.init_app(app)

# Create instance of DataManager for DB operations
data_manager = DataManager()

# Index route: displays all user (if any available) and user creation form
@app.route("/", methods=["GET"])
def index():
    """Render the homepage with a list of all users and a form to add new user"""
    try:
        users = data_manager.get_users()
    except SQLAlchemyError:
        flash("Database error: unable to load users.", "error")
        users = []
    return render_template("index.html", users=users)

# Add new user via form submission
@app.route("/users", methods=["POST"])
def add_user():
    """Handle form submission to create a new user and store it in the database."""
    name = request.form.get("name")
    if not name:
        flash("Please enter a name", "error")
        return redirect(url_for("index"))

    try:
        data_manager.create_user(name)
        flash(f"User '{name}' added successfully", "success")
    except Exception as e:
        flash("Error while adding user", "error")

    return redirect(url_for("index"))



# Show favorite movies of a specific user
@app.route("/users/<int:user_id>/movies", methods=["GET"])
def show_movies(user_id):
    """Display all movies associated with a specific user."""
    user = data_manager.get_user(user_id)
    if user is None:
        flash(f"User '{user_id}' not found", "error")
        return redirect(url_for("index"))

    movies = data_manager.get_movies(user_id)
    return render_template("movies.html", user=user, movies=movies)

# Add a new movie using OMDB API
@app.route("/users/<int:user_id>/movies", methods=["POST"])
def add_movie(user_id):
    """Add a new movie for a user by fetching data from the OMDb API."""
    title = request.form.get("title")
    if not title:
        flash("No title provided", "error")
        return redirect(url_for("show_movies", user_id=user_id))

    # Fetch movie data from OMDb API
    omdb_url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    try:
        response = requests.get(omdb_url, timeout=5)
        data = response.json()
    except requests.exceptions.RequestException as e:
        flash("Error fetching movie data.", "error")
        return redirect(url_for("show_movies", user_id=user_id))

    if data.get("Response") == "False":
        flash(f"Movie not: {title}", "error")
        return redirect(url_for("show_movies", user_id=user_id))

    # create a movie object and save to DB
    movie = Movie(
        name=data.get("Title"),
        year=data.get("Year"),
        director=data.get("Director"),
        poster_url=data.get("Poster"),
        user_id=user_id
    )

    try:
        data_manager.add_movie(movie)
        flash(f"Film '{movie.name}' added succsessfully.", "success")
    except Exception as e:
        flash("Error while saving movie", "error")

    return redirect(url_for("show_movies", user_id=user_id))


# Update a movie title
@app.route("/users/<int:user_id>/movies/<int:movie_id>/update", methods=["POST"])
def update_movie(user_id, movie_id):
    """Update a movie title only it it belongs to the current user"""
    new_title = request.form.get("title")
    movie = data_manager.get_movies(user_id, movie_id)

    if movie.user_id != user_id:
        flash(f"Unauthorized action !", "error")
        return redirect(url_for("show_movies", user_id=user_id))
    if new_title:
        data_manager.update_movie(movie_id, new_title)
    return redirect(url_for("show_movies", user_id=user_id))

# Delete a movie
@app.route("/users/<int:user_id>/movies/<int:movie_id>/delete", methods=["POST"])
def delete_movie(user_id, movie_id):
    """Delete a movie only if it belongs to the current user."""
    movie = data_manager.get_movie(movie_id)
    if movie.user_id != user_id:
        flash("Unauthorized action !", "error")
        return redirect(url_for("show_movies", user_id=user_id))
    data_manager.delete_movie(movie_id)
    return redirect(url_for("show_movies", user_id=user_id))

# Custom error page for 404
@app.errorhandler(404)
def page_not_found(e):
    """Render a custom 404 error page when a route is not found."""
    return render_template("404.html"), 404

# Custom error page for 500
@app.errorhandler(500)
def internal_error(e):
    """Render a custom 500 error page for internal server errors."""
    return render_template("500.html"), 500


# Creates database tables if not exist already
with app.app_context():
    db.create_all()

# Start Flask app
if __name__ == "__main__":
    app.run(debug=True, port=5002)


