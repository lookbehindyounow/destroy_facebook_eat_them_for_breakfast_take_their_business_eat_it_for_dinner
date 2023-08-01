from flask import render_template, redirect, Blueprint, request
from models import User, Friend, Friendship, Post, Comment, Approval
from app import db
from controllers.posts_controller import delete_post, delete_comment

users_blueprint=Blueprint("users",__name__)

@users_blueprint.route("/")
def login_page():
    return render_template("login.jinja")

@users_blueprint.route("/login",methods=["POST"])
def login():
    user=User.query.filter_by(name=request.form["name"],password=request.form["password"]).first()
    if user==None:
        if request.form["new_or_old"]=="new":
            user=User(name=request.form["name"],password=request.form["password"])
            db.session.add(user)
            db.session.commit()
            db.session.add(Friend(id=user.id))
            db.session.commit()
        else:
            return redirect("/") # MAKE AN INCORRECT PASSWORD MESSAGE
    return redirect(f"/{user.id}")

@users_blueprint.route("/<int:user_id>/users")
def show_users(user_id):
    users=User.query.all()
    friendships=Friendship.query.filter_by(user_id=user_id).all()
    friends_ids=[friendship.friend_id for friendship in friendships]
    return render_template("users.jinja",user_id=user_id,users=users,friends_ids=friends_ids)

@users_blueprint.route("/<int:user_id>/users/<int:friend_id>/add")
@users_blueprint.route("/<int:user_id>/profile/<int:friend_id>/add") # make this a recognnisable thing that redirects back to the profile page
def add_friend(user_id,friend_id):
    db.session.add(Friendship(user_id=user_id,friend_id=friend_id))
    db.session.add(Friendship(user_id=friend_id,friend_id=user_id))
    db.session.commit()
    return redirect(f"/{user_id}/users")

@users_blueprint.route("/<int:user_id>/users/<int:friend_id>/remove")
@users_blueprint.route("/<int:user_id>/profile/<int:friend_id>/remove") # make this a recognnisable thing that redirects back to the profile page
def remove_friend(user_id,friend_id):
    relations=Friendship.query.filter(((Friendship.user_id==user_id) & (Friendship.friend_id==friend_id)) |
                                    ((Friendship.user_id==friend_id) & (Friendship.friend_id==user_id))).all()
    [db.session.delete(friendship) for friendship in relations] # talk about incase duplicate friendship
    db.session.commit()
    return redirect(f"/{user_id}/users")

@users_blueprint.route("/<int:user_id>/profile/<int:profile_id>")
def show_profile(user_id,profile_id):
    profile=User.query.get(profile_id)
    profile.friends_list=User.query.join(Friendship).filter(profile_id==Friendship.friend_id).all()
    posts=Post.query.filter_by(user_id=profile_id).all()
    [post.set_variables() for post in posts]
    posts.sort(key=lambda post: post.time, reverse=True)
    return render_template("feed.jinja",user_id=user_id,profile=profile,posts=posts,isprofile=True)

@users_blueprint.route("/<int:user_id>/profile/delete")
def delete_profile(user_id):
    # talk about the order
    posts=Post.query.filter_by(user_id=user_id).all()
    [delete_post(user_id,post.id) for post in posts]
    comments=Comment.query.filter_by(user_id=user_id).all()
    [delete_comment(user_id,None,comment.id) for comment in comments] # talk about the None
    approvals=Approval.query.filter_by(user_id=user_id).all()
    [db.session.delete(approval) for approval in approvals]
    friendships=Friendship.query.filter((Friendship.user_id==user_id) | (Friendship.friend_id==user_id)).all()
    [db.session.delete(friendship) for friendship in friendships]
    friend=Friend.query.get(user_id)
    db.session.delete(friend)
    user=User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect("/")