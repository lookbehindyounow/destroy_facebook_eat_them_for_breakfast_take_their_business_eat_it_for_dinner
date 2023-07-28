from flask import render_template, redirect, Blueprint, request
from models import User, Post, Comment
from app import db
import datetime

users_blueprint=Blueprint("users",__name__)

@users_blueprint.route("/")
def login_page():
    return render_template("login.jinja")

@users_blueprint.route("/login",methods=["POST"])
def login():
    if request.form["radio"]=="new":
        user=User(name=request.form["name"],password=request.form["password"])
        db.session.add(user)
        db.session.commit()
    else:
        users=User.query.all()
        user=[user for user in users if user.name==request.form["name"] and user.password==request.form["password"]]
        if len(user)==0:
            return redirect("/")
        user=user[0]
    return redirect(f"/{user.id}")