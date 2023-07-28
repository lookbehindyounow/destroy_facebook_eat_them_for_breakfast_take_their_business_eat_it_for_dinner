from flask import Flask, render_template, redirect, Blueprint, request
from models import Game, User
from app import db
import datetime

users_blueprint=Blueprint("users",__name__)

@users_blueprint.route("/users")
def users():
    users=User.query.all() # sort this alphabetically if we add a user edit function
    return render_template("users.jinja",users=users)

@users_blueprint.route("/users/<id>")
def show_user(id):
    user=User.query.get(id)
    date=datetime.date.today()
    age=date.year - user.dob.year - ((date.month, date.day) < (user.dob.month, user.dob.day))
    all_games=Game.query.all()
    games=[game for game in all_games if game.user_id==id]
    return render_template("show_user.jinja",user=user,games=games,age=age)

@users_blueprint.route("/users/<id>/delete",methods=["POST"])
def delete_user(id):
    user=User.query.get(id)
    games=Game.query.all()
    user_games=[game for game in games if game.user_id==int(id)]
    [game.check_in() for game in user_games]
    db.session.delete(user)
    db.session.commit()
    return redirect("/users") # if users page is removed change this redirect to /games