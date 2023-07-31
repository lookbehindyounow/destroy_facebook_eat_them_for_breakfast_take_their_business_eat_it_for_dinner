from flask import render_template, redirect, Blueprint, request
from models import Post, Comment, Approval
from app import db
from datetime import datetime

posts_blueprint=Blueprint("posts",__name__)

@posts_blueprint.route("/<int:user_id>")
def show_feed(user_id):
    raw_posts=Post.query.all() # sort by time of last engagement (maybe just reverse the list, could edit a post's table entry & edit it right back to what it was each time a comment is made to 'bump' it down to the bottom of the posts table in the db)
    posts=[]
    for post in raw_posts:
        post.set_variables()
        post.get_comments()
        posts.append(post)
    return render_template("index.jinja",user_id=user_id,posts=posts)

@posts_blueprint.route("/<int:user_id>/<int:post_id>")
def show_post(user_id,post_id):
    post=Post.query.get(post_id)
    post.set_variables()
    comments=post.get_comments()
    return render_template("show_post.jinja",user_id=user_id,post=post,comments=comments)

@posts_blueprint.route("/<int:user_id>/new_post_form")
def new_post_form(user_id):
    return render_template("new.jinja",user_id=user_id,role="Post")

@posts_blueprint.route("/<int:user_id>",methods=["POST"])
def new_post(user_id):
    post=Post(user_id=user_id,time=datetime.now(),content=request.form["content"])
    db.session.add(post)
    db.session.commit()
    return redirect(f"/{user_id}")

@posts_blueprint.route("/<int:user_id>/<int:post_id>/new_comment_form")
def new_comment_form(user_id,post_id):
    post=Post.query.get(post_id)
    post.set_variables()
    comments=post.get_comments()
    return render_template("new.jinja",user_id=user_id,role="Comment",post=post,comments=comments)

@posts_blueprint.route("/<int:user_id>/<int:post_id>",methods=["POST"])
def new_comment(user_id,post_id):
    comment=Comment(user_id=user_id,post_id=post_id,time=datetime.now(),content=request.form["content"])
    db.session.add(comment)
    db.session.commit()
    return redirect(f"/{user_id}/{post_id}")

@posts_blueprint.route("/<int:user_id>/<int:post_id>/edit_post_form")
def edit_post_form(user_id,post_id):
    post=Post.query.get(post_id)
    return render_template("new.jinja",user_id=user_id,role="Update Post",post=post)

@posts_blueprint.route("/<int:user_id>/<int:post_id>/edit_post",methods=["POST"])
def edit_post(user_id,post_id):
    post=Post.query.get(post_id)
    post.content=request.form["content"]
    db.session.commit()
    return redirect(f"/{user_id}/{post_id}")

@posts_blueprint.route("/<int:user_id>/<int:post_id>/delete_post")
def delete_post(user_id,post_id):
    post=Post.query.get(post_id)
    comments=post.get_comments()
    [comment.set_variables() for comment in comments]
    [[db.session.delete(approval) for approval in comment.approvals] for comment in comments]
    [db.session.delete(comment) for comment in comments]
    db.session.delete(post)
    db.session.commit()
    return redirect(f"/{user_id}")

@posts_blueprint.route("/<int:user_id>/<int:post_id>/<int:comment_id>/edit_comment_form")
def edit_comment_form(user_id,post_id,comment_id):
    post=Post.query.get(post_id)
    post.set_variables()# move this up to above line?
    comments=post.get_comments()
    comment=Comment.query.get(comment_id)
    return render_template("new.jinja",user_id=user_id,role="Update Comment",post=post,comments=comments,comment=comment)

@posts_blueprint.route("/<int:user_id>/<int:post_id>/<int:comment_id>/edit_comment",methods=["POST"])
def edit_comment(user_id,post_id,comment_id):
    comment=Comment.query.get(comment_id)
    comment.content=request.form["content"]
    db.session.commit()
    return redirect(f"/{user_id}/{post_id}")

@posts_blueprint.route("/<int:user_id>/<int:post_id>/<int:comment_id>/delete_comment")
def delete_comment(user_id,post_id,comment_id):
    comment=Comment.query.get(comment_id)
    comment.set_variables()
    [db.session.delete(approval) for approval in comment.approvals]
    db.session.delete(comment)
    db.session.commit()
    return redirect(f"/{user_id}/{post_id}")

@posts_blueprint.route("/<int:user_id>/<int:post_id>/approve/<fromfeed>")
def approve_post(user_id,post_id,fromfeed):
    approvals=Approval.query.all()
    existing=[approval for approval in approvals if approval.user_id==user_id and approval.post_id==post_id]
    if len(existing)==0:
        approval=Approval(user_id=user_id,ispost=True,post_id=post_id)
        db.session.add(approval)
    else:
        db.session.delete(existing[0])
    db.session.commit()
    if bool(fromfeed):
        return redirect(f"/{user_id}")
    else:
        return redirect(f"{user_id}/{post_id}")

@posts_blueprint.route("/<int:user_id>/<int:post_id>/<int:comment_id>/approve")
def approve_comment(user_id,post_id,comment_id):
    approvals=Approval.query.all()
    existing=[approval for approval in approvals if approval.user_id==user_id and approval.comment_id==comment_id]
    if len(existing)==0:
        approval=Approval(user_id=user_id,ispost=False,comment_id=comment_id)
        db.session.add(approval)
    else:
        db.session.delete(existing[0])
    db.session.commit()
    return redirect(f"/{user_id}/{post_id}")