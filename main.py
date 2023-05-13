from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
MOVIE_DB_SEARCH_URL="https://developers.themoviedb.org/3/getting-started/introduction"
MOVIE_DB_API_KEY="thfrsyfhfeyfeyfegyqhf x3r"
db = SQLAlchemy(app)

class Movie(db.Model):
   
   id = db.Column(db.Integer, primary_key=True)
   title = db.Column(db.String(250), unique=True, nullable=False)
   year = db.Column(db.Integer, nullable=False)
   description = db.Column(db.String(500), nullable=False)
   rating = db.Column(db.Float, nullable=False)
   ranking = db.Column(db.Integer, nullable=False)
   reveiw = db.Column(db.String(250), nullable=False)
   img_url = db.Column(db.String(250), nullable=False)

db.create_all()

new_movie = Movie(
    title="Phone Booth",
    year=2002,
    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    rating=7.3,
    ranking=10,
    review="My favourite character was the caller.",
    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
 )

db.session.add(new_movie)
db.session.commit()

class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")
    


@app.route("/edit", methods=["GET", "POST"])
def rate_movie():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)

@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()  



@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    
    #This line loops through all the movies
    for i in range(len(all_movies)):
        #This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movie=new_movie)


class Add():
    title = StringField("add a movie")
    add_button=SubmitField("Add")



@app.route("/add", methods=["GET", "POST"])
def add_movie():
    form = Add()
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(MOVIE_D,B_SEARCH_URL params={"api_key": MOVIE_DB_API_KEY, "query": movie_title})
        detail = response.json(["result"])
        return render_template("select.html", option=detail)


    return render_template("add")


@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
        #The language parameter is optional, if you were making the website for a different audience 
        #e.g. Hindi speakers then you might choose "hi-IN"
        response = requests.get(movie_api_url, params={"api_key": MOVIE_DB_API_KEY, "language": "en-US"})
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            #The data in release_date includes month and day, we will want to get rid of.
            year=data["release_date"].split("-")[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("home"))





if __name__ == '__main__':
    app.run(debug=True)
