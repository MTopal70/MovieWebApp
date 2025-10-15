from flask import Flask, request, redirect, url_for, render_template, flash
from models import db, Movie, User
from data_manager import DataManager
from config import OMDB_API_KEY
import requests
import os

app = Flask(__name__)

# 🔧 Datenbank-Konfiguration
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "data", "moviweb.sqlite")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "supersecretkey"

# 📦 Datenbank initialisieren
db.init_app(app)

# 🧠 DataManager initialisieren
data_manager = DataManager()

# 🏠 Startseite: Liste aller User + Formular
@app.route("/", methods=["GET"])
def index():
    users = data_manager.get_users()
    return render_template("index.html", users=users)

# ➕ Neuen User hinzufügen
@app.route("/users", methods=["POST"])
def add_user():
    name = request.form.get("name")
    if not name:
        flash("Bitte gib einen Namen ein.", "error")
        return redirect(url_for("index"))

    try:
        data_manager.create_user(name)
        flash(f"User '{name}' wurde erfolgreich hinzugefügt.", "success")
    except Exception as e:
        flash("Fehler beim Speichern des Users.", "error")

    return redirect(url_for("index"))



# 🎬 Lieblingsfilme eines Users anzeigen
@app.route("/users/<int:user_id>/movies", methods=["GET"])
def show_movies(user_id):
    user = data_manager.get_user(user_id)
    movies = data_manager.get_movies(user_id)
    return render_template("movies.html", user=user, movies=movies)



# ➕ Neuen Film hinzufügen (mit OMDb)

@app.route("/users/<int:user_id>/movies", methods=["POST"])
def add_movie(user_id):
    title = request.form.get("title")
    if not title:
        flash("Kein Titel angegeben.", "error")
        return redirect(url_for("show_movies", user_id=user_id))

    # 🔍 OMDb-API abfragen mit Fehlerbehandlung
    omdb_url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    try:
        response = requests.get(omdb_url, timeout=5)
        data = response.json()
    except requests.exceptions.RequestException as e:
        flash("Fehler beim Abrufen der Filmdaten.", "error")
        return redirect(url_for("show_movies", user_id=user_id))

    if data.get("Response") == "False":
        flash(f"Film nicht gefunden: {title}", "error")
        return redirect(url_for("show_movies", user_id=user_id))

    # 🎬 Movie-Objekt erstellen
    movie = Movie(
        name=data.get("Title"),
        year=data.get("Year"),
        director=data.get("Director"),
        poster_url=data.get("Poster"),
        user_id=user_id
    )

    # 💾 In Datenbank speichern mit Fehlerbehandlung
    try:
        data_manager.add_movie(movie)
        flash(f"Film '{movie.name}' erfolgreich hinzugefügt.", "success")
    except Exception as e:
        flash("Fehler beim Speichern des Films.", "error")

    return redirect(url_for("show_movies", user_id=user_id))



# ✏️ Film aktualisieren
@app.route("/users/<int:user_id>/movies/<int:movie_id>/update", methods=["POST"])
def update_movie(user_id, movie_id):
    new_title = request.form.get("title")
    if new_title:
        data_manager.update_movie(movie_id, new_title)
    return redirect(url_for("show_movies", user_id=user_id))

# ❌ Film löschen
@app.route("/users/<int:user_id>/movies/<int:movie_id>/delete", methods=["POST"])
def delete_movie(user_id, movie_id):
    data_manager.delete_movie(movie_id)
    return redirect(url_for("show_movies", user_id=user_id))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template("500.html"), 500


# 🛠️ Datenbanktabellen erstellen
with app.app_context():
    db.create_all()

# 🚀 App starten
if __name__ == "__main__":
    app.run(debug=True, port=5002)


