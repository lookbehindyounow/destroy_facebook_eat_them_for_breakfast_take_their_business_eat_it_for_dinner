from flask import render_template, redirect, Blueprint, request
from models import Game, User
from app import db
import datetime

games_blueprint=Blueprint("games",__name__)

@games_blueprint.route("/games")
def games():
    games=Game.query.all() # sort this alphabetically
    return render_template("index.jinja",games=games)

@games_blueprint.route("/games/<id>")
def show_game(id):
    users=User.query.all()
    game=Game.query.get(id)
    if game.user_id is not None:
        game_user=User.query.get(game.user_id)
    else:
        game_user=None
        date=datetime.date.today()
        all_users=users
        users=[]
        for user in all_users:
            age=date.year - user.dob.year - ((date.month, date.day) < (user.dob.month, user.dob.day))
            if age>=game.age_rating:
                users.append(user)
    return render_template("show_game.jinja",game=game,users=users,game_user=game_user)

@games_blueprint.route("/games/<id>/delete",methods=["POST"])
def delete_game(id):
    game=Game.query.get(id)
    db.session.delete(game)
    db.session.commit()
    return redirect("/games")

@games_blueprint.route("/games/<id>/check_out",methods=["POST"])
def check_out(id):
    user_id=request.form["user"]
    user=User.query.get(user_id)
    game=Game.query.get(id)
    game.check_out(user_id)
    db.session.commit()
    return redirect(f"/games/{id}")

@games_blueprint.route("/games/<id>/check_in",methods=["POST"])
def check_in(id):
    game=Game.query.get(id)
    game.check_in()
    db.session.commit()
    return redirect(f"/games/{id}")

@games_blueprint.route("/games/new")
def new_game_form():
    return render_template("new_game.jinja")

@games_blueprint.route("/games",methods=["POST"])
def add_game():
    game=Game(title=request.form["title"],
              genre=request.form["genre"],
              description=request.form["description"],
              age_rating=request.form["age_rating"]
    )
    db.session.add(game)
    db.session.commit()
    return redirect("/games")