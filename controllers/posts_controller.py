from flask import render_template, redirect, Blueprint, request
from models import Post, Comment
from app import db
import datetime

posts_blueprint=Blueprint("posts",__name__)

@posts_blueprint.route("/")
def feed():
    posts=Post.query.all() # sort by time of last engagement (maybe just reverse the list, could edit a post's table entry & edit it right back to what it was each time a comment is made to 'bump' it down to the bottom of the posts table in the db)
    comments=Comment.query.all()
    print(comments)
    return render_template("index.jinja",posts=posts)