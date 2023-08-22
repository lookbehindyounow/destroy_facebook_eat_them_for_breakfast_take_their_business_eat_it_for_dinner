from flask import render_template, redirect, Blueprint, request
from models import User, Post, Comment, Approval, Friendship
from app import db
from datetime import datetime # for new_post() & new_comment()

posts_blueprint=Blueprint("posts",__name__)

@posts_blueprint.route("/<int:user_id>")
def show_feed(user_id): # home feed page
    # queries for posts that should show up
    friends_posts=Post.query.join(Friendship, Post.user_id==Friendship.friend_id).filter(user_id==Friendship.user_id).all()
    my_posts_and_public_posts=Post.query.filter((Post.user_id==user_id) | Post.public).all()
    posts=list(set(friends_posts+my_posts_and_public_posts)) # add results & remove duplicates
    [post.set_variables() for post in posts] # load any needed display information into post objects
    # sort shown posts by the most recent time in the post's time & any of it's comments' times
    posts.sort(key=lambda post: max([post.time]+[comment.time for comment in post.comments]), reverse=True)
    user=User.query.get(user_id) # get user
    user.roulette.wheel=True # set attributes in user's roulette object (unfinished feature but these
    user.roulette.ball=True # booleans need to be true for the wheel & ball to spin)
    # because isprofile=False, feed.jinja will extend index.jinja
    return render_template("feed.jinja",user_id=user_id,posts=posts,isprofile=False,roulette=user.roulette)

@posts_blueprint.route("/<int:user_id>/<int:post_id>")
def show_post(user_id,post_id): # post page
    post=Post.query.get(post_id)
    post.set_variables() # load display information
    return render_template("post.jinja",user_id=user_id,post=post)

@posts_blueprint.route("/<int:user_id>/new_post_form")
def new_post_form(user_id): # loads new.jinja with role="Post"
    return render_template("composite/new.jinja",user_id=user_id,role="Post")

@posts_blueprint.route("/<int:user_id>",methods=["POST"])
def new_post(user_id): # create new post
    post=Post(user_id=user_id,time=datetime.now(),public=("public" in request.form),content=request.form["content"])
    db.session.add(post)
    db.session.commit()
    return redirect(f"/{user_id}") # redirect to home feed

@posts_blueprint.route("/<int:user_id>/<int:post_id>/new_comment_form")
def new_comment_form(user_id,post_id): # loads new.jinja with role="Comment", extending post.jinja
    post=Post.query.get(post_id) # so we need the post, because it will be displayed too
    post.set_variables()
    return render_template("composite/new.jinja",user_id=user_id,role="Comment",post=post)

@posts_blueprint.route("/<int:user_id>/<int:post_id>",methods=["POST"])
def new_comment(user_id,post_id): # create new comment
    comment=Comment(user_id=user_id,post_id=post_id,time=datetime.now(),content=request.form["content"])
    db.session.add(comment)
    db.session.commit()
    return redirect(f"/{user_id}/{post_id}") # redirect to parent post's page

@posts_blueprint.route("/<int:user_id>/<int:post_id>/edit_post_form")
def edit_post_form(user_id,post_id): # loads new.jinja with role="Update Post"
    post=Post.query.get(post_id) # we need the post that's being edited, but we don't need the
                                # display information from post.set_variables()
    return render_template("composite/new.jinja",user_id=user_id,role="Update Post",post=post)

@posts_blueprint.route("/<int:user_id>/<int:post_id>/edit_post",methods=["POST"])
def edit_post(user_id,post_id): # edit existing post
    post=Post.query.get(post_id)
    post.edit(request.form["content"],("public" in request.form))
    return redirect(f"/{user_id}/{post_id}") # redirect to post's page

@posts_blueprint.route("/<int:user_id>/<int:post_id>/<int:comment_id>/edit_comment_form")
def edit_comment_form(user_id,post_id,comment_id): # loads new.jinja with role="Update Comment"
    post=Post.query.get(post_id) # post will be displayed
    post.set_variables()
    comment=Comment.query.get(comment_id) # comment object that's being edited
    return render_template("composite/new.jinja",user_id=user_id,role="Update Comment",post=post,comment=comment)

@posts_blueprint.route("/<int:user_id>/<int:post_id>/<int:comment_id>/edit_comment",methods=["POST"])
def edit_comment(user_id,post_id,comment_id): # edit existing comment
    comment=Comment.query.get(comment_id)
    comment.edit(request.form["content"])
    return redirect(f"/{user_id}/{post_id}") # redirect to parent post's page

@posts_blueprint.route("/<int:user_id>/<int:post_id>/delete_post")
def delete_post(user_id,post_id):
    post=Post.query.get(post_id)
    post.set_variables() # get comments & approvals
    [db.session.delete(approval) for approval in post.approvals] # cascading delete to keep database tidy
    [[db.session.delete(approval) for approval in comment.approvals] for comment in post.comments]
    [db.session.delete(comment) for comment in post.comments]
    db.session.delete(post)
    db.session.commit()
    return redirect(f"/{user_id}") # redirect to home feed

@posts_blueprint.route("/<int:user_id>/<int:post_id>/<int:comment_id>/delete_comment")
def delete_comment(user_id,post_id,comment_id):
    comment=Comment.query.get(comment_id)
    comment.set_variables() # get approvals
    [db.session.delete(approval) for approval in comment.approvals] # cascade
    db.session.delete(comment)
    db.session.commit()
    return redirect(f"/{user_id}/{post_id}") # redirect to parent post's page

@posts_blueprint.route("/<int:user_id>/<int:post_id>/approve/<int:be_where>") # approving post
@posts_blueprint.route("/<int:user_id>/<int:post_id>/<int:comment_id>/approve") # approving comment
def approve(user_id,post_id,comment_id=None,be_where=0):
    if comment_id==None: # if you've approved a post
        approvals=Approval.query.filter_by(user_id=user_id,post_id=post_id).all()
    else: # if you've approved a comment
        approvals=Approval.query.filter_by(user_id=user_id,comment_id=comment_id).all()
    if len(approvals)==0: # if current user has no approvals for this post/comment
        if comment_id==None: # create approval record for post/comment
            approval=Approval(user_id=user_id,ispost=True,post_id=post_id)
        else:
            approval=Approval(user_id=user_id,ispost=False,comment_id=comment_id)
        db.session.add(approval)
    else: # if current user has approvals for this post/comment (should only be 1):
        [db.session.delete(approval) for approval in approvals] # remove them all (unapprove)
    db.session.commit()
    if be_where==1: # if approving from a profile feed, redirect to said profile feed
        profile_id=Post.query.get(post_id).user_id
        return redirect(f"/{user_id}/profile/{profile_id}")
    elif be_where==2: # if approving from home feed, redirect to home feed
        return redirect(f"/{user_id}")
    else: # otherwise, redirect to post page
        return redirect(f"/{user_id}/{post_id}")