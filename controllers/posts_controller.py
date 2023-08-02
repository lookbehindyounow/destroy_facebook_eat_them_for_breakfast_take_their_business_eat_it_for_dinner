from flask import render_template, redirect, Blueprint, request
from models import Post, Comment, Approval, Friendship
from app import db
from datetime import datetime

posts_blueprint=Blueprint("posts",__name__)

@posts_blueprint.route("/<int:user_id>")
def show_feed(user_id):
    friends_posts=Post.query.join(Friendship, Post.user_id==Friendship.friend_id).filter(user_id==Friendship.user_id).all()
    my_posts_and_public_posts=Post.query.filter((Post.user_id==user_id) | Post.public).all()
    # talk about these queries & the duplicate removal below
    posts=list(set(friends_posts+my_posts_and_public_posts))
    [post.set_variables() for post in posts]
    posts.sort(key=lambda post: max([post.time]+[comment.time for comment in post.comments]), reverse=True)
    # talk about this^ sort
    return render_template("feed.jinja",user_id=user_id,posts=posts,isprofile=False)

@posts_blueprint.route("/<int:user_id>/<int:post_id>")
def show_post(user_id,post_id):
    post=Post.query.get(post_id)
    post.set_variables()
    return render_template("post.jinja",user_id=user_id,post=post)

@posts_blueprint.route("/<int:user_id>/new_post_form")
def new_post_form(user_id):
    return render_template("composite/new.jinja",user_id=user_id,role="Post")

@posts_blueprint.route("/<int:user_id>",methods=["POST"])
def new_post(user_id):
    post=Post(user_id=user_id,time=datetime.now(),public=("public" in request.form),content=request.form["content"])
    db.session.add(post)
    db.session.commit()
    return redirect(f"/{user_id}")

@posts_blueprint.route("/<int:user_id>/<int:post_id>/new_comment_form")
def new_comment_form(user_id,post_id):
    post=Post.query.get(post_id)
    post.set_variables()
    return render_template("composite/new.jinja",user_id=user_id,role="Comment",post=post)

@posts_blueprint.route("/<int:user_id>/<int:post_id>",methods=["POST"])
def new_comment(user_id,post_id):
    comment=Comment(user_id=user_id,post_id=post_id,time=datetime.now(),content=request.form["content"])
    db.session.add(comment)
    db.session.commit()
    return redirect(f"/{user_id}/{post_id}")

@posts_blueprint.route("/<int:user_id>/<int:post_id>/edit_post_form")
def edit_post_form(user_id,post_id):
    post=Post.query.get(post_id)
    post.set_variables()
    return render_template("composite/new.jinja",user_id=user_id,role="Update Post",post=post)

@posts_blueprint.route("/<int:user_id>/<int:post_id>/edit_post",methods=["POST"])
def edit_post(user_id,post_id):
    post=Post.query.get(post_id)
    post.edit(request.form["content"],("public" in request.form))
    return redirect(f"/{user_id}/{post_id}")

@posts_blueprint.route("/<int:user_id>/<int:post_id>/delete_post")
def delete_post(user_id,post_id):
    post=Post.query.get(post_id)
    post.set_variables()
    # talk about the order
    [db.session.delete(approval) for approval in post.approvals]
    [[db.session.delete(approval) for approval in comment.approvals] for comment in post.comments]
    [db.session.delete(comment) for comment in post.comments]
    db.session.delete(post)
    db.session.commit()
    return redirect(f"/{user_id}")

@posts_blueprint.route("/<int:user_id>/<int:post_id>/<int:comment_id>/edit_comment_form")
def edit_comment_form(user_id,post_id,comment_id):
    post=Post.query.get(post_id)
    post.set_variables()
    comment=Comment.query.get(comment_id)
    return render_template("composite/new.jinja",user_id=user_id,role="Update Comment",post=post,comment=comment)

@posts_blueprint.route("/<int:user_id>/<int:post_id>/<int:comment_id>/edit_comment",methods=["POST"])
def edit_comment(user_id,post_id,comment_id):
    comment=Comment.query.get(comment_id)
    comment.edit(request.form["content"])
    return redirect(f"/{user_id}/{post_id}")

@posts_blueprint.route("/<int:user_id>/<int:post_id>/<int:comment_id>/delete_comment")
def delete_comment(user_id,post_id,comment_id):
    comment=Comment.query.get(comment_id)
    comment.set_variables()
    [db.session.delete(approval) for approval in comment.approvals]
    db.session.delete(comment)
    db.session.commit()
    return redirect(f"/{user_id}/{post_id}")

@posts_blueprint.route("/<int:user_id>/<int:post_id>/approve/<int:fromfeed>")
@posts_blueprint.route("/<int:user_id>/<int:post_id>/<int:comment_id>/approve")
def approve(user_id,post_id,comment_id=None,fromfeed=False):
    if comment_id==None:
        approvals=Approval.query.filter_by(user_id=user_id,post_id=post_id).all()
    else:
        approvals=Approval.query.filter_by(user_id=user_id,comment_id=comment_id).all()
    if len(approvals)==0:
        if comment_id==None:
            approval=Approval(user_id=user_id,ispost=True,post_id=post_id)
        else:
            approval=Approval(user_id=user_id,ispost=False,comment_id=comment_id)
        db.session.add(approval)
    else:
        [db.session.delete(approval) for approval in approvals] # talk about incase duplicate approval
    db.session.commit()
    if fromfeed: # talk about this condition
        return redirect(f"/{user_id}")
    return redirect(f"/{user_id}/{post_id}")