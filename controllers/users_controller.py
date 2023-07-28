from flask import render_template, redirect, Blueprint, request
from models import User, Post, Comment
from app import db
import datetime

users_blueprint=Blueprint("users",__name__)

@users_blueprint.route("/")
def login_page():
    return render_template("login.jinja")

@users_blueprint.route("/login")
def login():
    users=User.query.all()
    user=[user for user in users if user.name==request.form["name"] and user.password==request.form["password"]]
    if len(user)==0:
        return redirect("/")
    else:
        return redirect(f"/{user[0].id}")