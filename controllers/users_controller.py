from flask import render_template, redirect, Blueprint, request
from models import User, Friend, Friendship, Post, Comment, Approval
from app import db
from controllers.posts_controller import delete_post, delete_comment

users_blueprint=Blueprint("users",__name__)
login_message=False

@users_blueprint.route("/")
@users_blueprint.route("/new_user")
def login_page():
    global login_message
    temp_message=login_message
    login_message=False
    if str(request.url_rule)=="/":
        new=False
        passwords=[user.password for user in User.query.all()]
    else:
        new=True
        passwords=[]
    return render_template("login.jinja",new=new,login_message=temp_message,passwords=passwords)

@users_blueprint.route("/login",methods=["POST"])
def login():
    user=User.query.filter_by(name=request.form["name"],password=request.form["password"]).first()
    if user==None:
        global login_message
        login_message=True
        return redirect("/")
    return redirect(f"/{user.id}")

@users_blueprint.route("/signup",methods=["POST"])
def signup():
    if User.query.filter_by(name=request.form["name"],password=request.form["password"]).all():
        global login_message
        login_message=True
        return redirect("/new_user")
    user=User(name=request.form["name"],password=request.form["password"])
    db.session.add(user)
    db.session.commit()
    db.session.add(Friend(id=user.id))
    db.session.commit()
    return redirect(f"/{user.id}")

@users_blueprint.route("/<int:user_id>/users")
def show_users(user_id):
    users=User.query.all()
    friendships=Friendship.query.filter_by(user_id=user_id).all()
    friends_ids=[friendship.friend_id for friendship in friendships]
    return render_template("users.jinja",user_id=user_id,users=users,friends_ids=friends_ids)

@users_blueprint.route("/<int:user_id>/users/<int:profile_id>/add")
@users_blueprint.route("/<int:user_id>/profile/<int:profile_id>/add")
def add_friend(user_id,profile_id):
    db.session.add(Friendship(user_id=user_id,friend_id=profile_id))
    db.session.add(Friendship(user_id=profile_id,friend_id=user_id))
    db.session.commit()
    if "users" in str(request.url_rule): # talk about this condition
        return redirect(f"/{user_id}/users")
    return redirect(f"/{user_id}/profile/{profile_id}")

@users_blueprint.route("/<int:user_id>/users/<int:profile_id>/remove")
@users_blueprint.route("/<int:user_id>/profile/<int:profile_id>/remove")
def remove_friend(user_id,profile_id):
    relations=Friendship.query.filter(((Friendship.user_id==user_id) & (Friendship.friend_id==profile_id)) |
                                    ((Friendship.user_id==profile_id) & (Friendship.friend_id==user_id))).all()
    [db.session.delete(friendship) for friendship in relations] # talk about incase duplicate friendship
    db.session.commit()
    if "users" in str(request.url_rule):
        return redirect(f"/{user_id}/users")
    return redirect(f"/{user_id}/profile/{profile_id}")

@users_blueprint.route("/<int:user_id>/profile/<int:profile_id>")
def show_profile(user_id,profile_id):
    profile=User.query.get(profile_id)
    profile.friends_list=User.query.join(Friendship).filter(profile_id==Friendship.friend_id).all()
    if Friendship.query.filter_by(user_id=user_id,friend_id=profile_id).all() or user_id==profile_id:
        posts=Post.query.filter_by(user_id=profile_id).all()
    else:
        posts=Post.query.filter_by(user_id=profile_id,public=True).all()
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