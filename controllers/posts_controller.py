from flask import render_template, redirect, Blueprint, request
from models import User, Post, Comment
from app import db
import datetime # add time to posts & comments

posts_blueprint=Blueprint("posts",__name__)

@posts_blueprint.route("/<user_id>")
def feed(user_id):
    posts_no_comments=Post.query.all() # sort by time of last engagement (maybe just reverse the list, could edit a post's table entry & edit it right back to what it was each time a comment is made to 'bump' it down to the bottom of the posts table in the db)
    posts=[[post,post.return_name(),post.count_comments()] for post in posts_no_comments]
    return render_template("index.jinja",user_id=user_id,posts=posts)

@posts_blueprint.route("/<user_id>/<post_id>")
def show_post(user_id,post_id):
    post=Post.query.get(post_id)
    author=post.return_name()
    comments=post.get_comments()
    return render_template("show_post.jinja",user_id=user_id,post=post,author=author,comments=comments)

@posts_blueprint.route("/<user_id>/new_post")
def post_form(user_id):
    return render_template("new.jinja",user_id=user_id,post=None)

@posts_blueprint.route("/<user_id>",methods=["POST"])
def post_post(user_id):
    post=Post(user_id=user_id,content=request.form["content"])
    db.session.add(post)
    db.session.commit()
    return redirect(f"/{user_id}")

@posts_blueprint.route("/<user_id>/<post_id>/new_comment")
def comment_form(user_id,post_id):
    post=Post.query.get(post_id)
    comments=post.get_comments()
    return render_template("new.jinja",user_id=user_id,post=post,comments=comments)

@posts_blueprint.route("/<user_id>/<post_id>",methods=["POST"])
def post_comment(user_id,post_id):
    comment=Comment(user_id=user_id,post_id=post_id,content=request.form["content"])
    db.session.add(comment)
    db.session.commit()
    return redirect(f"/{user_id}/{post_id}")