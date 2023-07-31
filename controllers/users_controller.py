from flask import render_template, redirect, Blueprint, request
from models import User, Friend, Friendship
from app import db

users_blueprint=Blueprint("users",__name__)

@users_blueprint.route("/")
def login_page():
    return render_template("login.jinja")

@users_blueprint.route("/login",methods=["POST"])
def login():
    if request.form["new_or_old"]=="new":
        user=User(name=request.form["name"],password=request.form["password"])
        db.session.add(user)
        db.session.commit()
        users=User.query.all() # SQL THING
        users.sort(key=lambda user: user.id, reverse=True)
        friend=Friend(id=users[0].id)
        db.session.add(friend)
        db.session.commit()
    else:
        users=User.query.all()
        user=[user for user in users if user.name==request.form["name"] and user.password==request.form["password"]]
        if len(user)==0:
            return redirect("/")
        user=user[0]
    return redirect(f"/{user.id}")

@users_blueprint.route("/<int:user_id>/users")
def show_users(user_id):
    users=User.query.all()
    myself=[user for user in users if user_id==user.id][0]
    users.remove(myself)
    friendships=Friendship.query.all() # SQL ting
    my_friends=[friendship.friend_id for friendship in friendships if friendship.user_id==user_id]
    print(users)
    return render_template("users.jinja",user_id=user_id,users=users,my_friends=my_friends)

@users_blueprint.route("/<int:user_id>/users/<int:friend_id>")
def add_or_remove_friend(user_id,friend_id):
    all_friendships=Friendship.query.all() # SQLLLLLL
    my_friends=[friendship.friend_id for friendship in all_friendships if friendship.user_id==user_id]
    if friend_id in my_friends:
        friendships=[friendship for friendship in all_friendships if
                    (friendship.user_id==user_id and friendship.friend_id==friend_id) or
                    (friendship.user_id==friend_id and friendship.friend_id==user_id)]
        db.session.delete(friendships[0])
        db.session.delete(friendships[1])
    else:
        friendships=[Friendship(user_id=user_id,friend_id=friend_id),
                    Friendship(user_id=friend_id,friend_id=user_id)
        ]
        db.session.add(friendships[0])
        db.session.add(friendships[1])
    db.session.commit()
    return redirect(f"/{user_id}/users")