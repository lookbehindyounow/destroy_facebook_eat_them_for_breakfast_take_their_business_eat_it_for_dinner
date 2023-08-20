from flask import render_template, redirect, Blueprint, request
from models import User, Friend, Friendship, Post, Comment, Approval
from app import db
from controllers.posts_controller import delete_post, delete_comment # for delete_profile()
from base64 import b64encode # for profile_pic()

users_blueprint=Blueprint("users",__name__)
login_message=False # initialise login message control boolean because it needs to exist already

@users_blueprint.route("/")
@users_blueprint.route("/new_user")
def login_page(): # login/signup page depending on route
    global login_message
    # if login_message has been set to true then it will be passed to login.jinja as temp_message
    # which controls whether a message shows indicating a login/signup problem 
    temp_message=login_message
    login_message=False
    if str(request.url_rule)=="/": # if route is "/"
        new=False # boolean controls login.jinja
        passwords=[user.password for user in User.query.all()] # passwords for dropdown menu
    else: # if route is "/new_user"
        new=True
        passwords=[]
    return render_template("login.jinja",new=new,login_message=temp_message,passwords=passwords)

@users_blueprint.route("/login",methods=["POST"])
def login(): # existing users
    # get first (should only be one) user  with matching username & password
    user=User.query.filter_by(name=request.form["name"],password=request.form["password"]).first()
    if user==None: # if no matching user
        global login_message
        login_message=True
        return redirect("/") # redirect to login_page() with global login_message set to True
    return redirect(f"/{user.id}") # otherwise redirect to user's home feed

@users_blueprint.route("/signup",methods=["POST"])
def signup(): # new users
    # get all (should be one or none) users with matching username & password, if exists:
    if User.query.filter_by(name=request.form["name"],password=request.form["password"]).all():
        global login_message
        login_message=True
        return redirect("/new_user") # redirect to login_page() with global login_message set to True
    user=User(name=request.form["name"],password=request.form["password"]) # otherwise create user
    db.session.add(user)
    db.session.commit()
    # matching record in friends table for friendships relationship table to work
    db.session.add(Friend(id=user.id))
    db.session.commit()
    return redirect(f"/{user.id}") # redirect to user's home feed

@users_blueprint.route("/<int:user_id>/users")
def show_users(user_id): # list of all users page
    users=User.query.all()
    # find ids of profiles with a friendship record with current user to identify in jinja who is a friend
    friends_ids=Friendship.query.filter_by(user_id=user_id).with_entities(Friendship.friend_id).all()
    friends_ids=[friend_id[0] for friend_id in friends_ids] # get ids from list of [(id, ),(id, ),(id, )...]
    return render_template("users/users.jinja",user_id=user_id,users=users,friends_ids=friends_ids)

@users_blueprint.route("/<int:user_id>/users/<int:profile_id>/add")
@users_blueprint.route("/<int:user_id>/profile/<int:profile_id>/add")
def add_friend(user_id,profile_id):
    db.session.add(Friendship(user_id=user_id,friend_id=profile_id)) # two records for each friendship, one
    db.session.add(Friendship(user_id=profile_id,friend_id=user_id)) # each way round for simpler querying
    db.session.commit()
    if "users" in str(request.url_rule): # if route includes "users"; meaning we came from users list page
        return redirect(f"/{user_id}/users") # redirect to users list
    # otherwise redirect to whatever profile page we came from
    return redirect(f"/{user_id}/profile/{profile_id}")

@users_blueprint.route("/<int:user_id>/users/<int:profile_id>/remove")
@users_blueprint.route("/<int:user_id>/profile/<int:profile_id>/remove")
def remove_friend(user_id,profile_id):
    # find all friendship records between current user & profile in question, just incase of duplicates
    # also have to find any matching records both ways round because there are two records for each friendship
    relations=Friendship.query.filter(((Friendship.user_id==user_id) & (Friendship.friend_id==profile_id)) |
                                    ((Friendship.user_id==profile_id) & (Friendship.friend_id==user_id))).all()
    [db.session.delete(friendship) for friendship in relations] # delete all records found
    db.session.commit()
    if "users" in str(request.url_rule):
        return redirect(f"/{user_id}/users")
    return redirect(f"/{user_id}/profile/{profile_id}")

@users_blueprint.route("/<int:user_id>/profile/<int:profile_id>")
def show_profile(user_id,profile_id): # profile page
    profile=User.query.get(profile_id)
    # find profile's friends
    profile.friends_list=User.query.join(Friendship).filter(profile_id==Friendship.friend_id).all()
    if Friendship.query.filter_by(user_id=user_id,friend_id=profile_id).all() or user_id==profile_id:
        # if selected profile is current user or a friend of current user, show all of profile's posts in feed
        posts=Post.query.filter_by(user_id=profile_id).all()
    else:
        # if not, show only public posts from profile
        posts=Post.query.filter_by(user_id=profile_id,public=True).all()
    [post.set_variables() for post in posts] # load any needed display information into post objects
    posts.sort(key=lambda post: post.time, reverse=True) # sort by time posted
    # because isprofile=True, feed.jinja will extend profile.jinja
    return render_template("feed.jinja",user_id=user_id,profile=profile,posts=posts,isprofile=True)

@users_blueprint.route("/<int:user_id>/profile/pfp",methods=["POST"])
def profile_pic(user_id): # upload pfp
    user=User.query.get(user_id)
    # get file submitted to form in profile page (only available if it's current user's profile)
    binary_pfp=request.files["profile_picture"].read()
    user.pfp=b64encode(binary_pfp).decode("utf-8") # convert binary to base 64 & save to users table
    db.session.commit()
    return redirect(f"/{user_id}/profile/{user_id}") # redirect to same page

@users_blueprint.route("/<int:user_id>/profile/delete")
def delete_profile(user_id):
    posts=Post.query.filter_by(user_id=user_id).all() # get all of user's posts
    [delete_post(user_id,post.id) for post in posts] # delete_post() cascades to child comments & approvals
    comments=Comment.query.filter_by(user_id=user_id).all() # get all comments
    [delete_comment(user_id,None,comment.id) for comment in comments] # also cascades
    approvals=Approval.query.filter_by(user_id=user_id).all() # approvals
    [db.session.delete(approval) for approval in approvals]
    # all friendships including user's id on either side
    friendships=Friendship.query.filter((Friendship.user_id==user_id) | (Friendship.friend_id==user_id)).all()
    [db.session.delete(friendship) for friendship in friendships]
    friend=Friend.query.get(user_id) # user's record in the friends table
    db.session.delete(friend)
    user=User.query.get(user_id) # user's record in the user table
    db.session.delete(user)
    db.session.commit()
    return redirect("/new_user") # redirect to signup page