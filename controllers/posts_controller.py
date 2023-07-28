from flask import render_template, redirect, Blueprint, request
from models import Post, Comment
from app import db
import datetime

posts_blueprint=Blueprint("posts",__name__)

@posts_blueprint.route("/")
def feed():
    posts_no_comments=Post.query.all() # sort by time of last engagement (maybe just reverse the list, could edit a post's table entry & edit it right back to what it was each time a comment is made to 'bump' it down to the bottom of the posts table in the db)
    posts=[[post,post.count_comments()] for post in posts_no_comments]
    return render_template("index.jinja",posts=posts)

@posts_blueprint.route("/<id>")
def show_post(id):
    post=Post.query.get(id)
    comments=post.get_comments()
    return render_template("show_post.jinja",post=post,comments=comments)