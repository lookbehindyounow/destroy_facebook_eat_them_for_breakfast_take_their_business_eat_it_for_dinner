from flask import render_template, redirect, Blueprint, request
from models import Post
from app import db
import datetime

posts_blueprint=Blueprint("posts",__name__)

@posts_blueprint.route("/")
def feed():
    return "workig?"