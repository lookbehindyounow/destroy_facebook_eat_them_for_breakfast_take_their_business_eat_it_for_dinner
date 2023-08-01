from app import db
from models import User, Friend, Friendship, Post, Comment, Approval
import click
from flask.cli import with_appcontext
from datetime import datetime

@click.command(name='seed')
@with_appcontext
def seed():
    Approval.query.delete()
    Comment.query.delete()
    Post.query.delete()
    Friendship.query.delete()
    Friend.query.delete()
    User.query.delete()
    
    users=[User(name="kev",password="kev123"),
        User(name="dan",password="password"),
        User(name="shelly",password="meow")]
    [db.session.add(user) for user in users]
    
    users=User.query.all()
    kev_id=[user.id for user in users if user.name=="kev"][0]
    dan_id=[user.id for user in users if user.name=="dan"][0]
    shelly_id=[user.id for user in users if user.name=="shelly (my cat)"][0]
    
    [db.session.add(Friend(id=user.id)) for user in users]
    
    friendships=[Friendship(user_id=kev_id,friend_id=shelly_id),Friendship(user_id=shelly_id,friend_id=kev_id),
                Friendship(user_id=shelly_id,friend_id=dan_id),Friendship(user_id=dan_id,friend_id=shelly_id)]
    [db.session.add(friendship) for friendship in friendships]
    
    posts=[Post(user_id=kev_id,time=datetime.now(),public=True,content="come on football yass 3 nil"),
        Post(user_id=dan_id,time=datetime.now(),public=True,content="nobody dm goin thru it"),
        Post(user_id=shelly_id,time=datetime.now(),public=False,content="if you do not share this post your mother will die in her sleep tonight there used to be a little girl who was scared of the dark she did not retweet this message & then later that night in her room there was a presence at the end of her bed she was never heard from again I do not give personcatalog permission to use my data or my photos COPY & PASTE THI S MESSAGE IT LEGAL BONDAGE CONTRACT IT WORKS NO REALLY")]
    [db.session.add(post) for post in posts]
    
    posts=Post.query.all()
    footy_id=[post.id for post in posts if post.content[0]=="c"][0]
    nodm_id=[post.id for post in posts if post.content[0]=="n"][0]
    chainmail_id=[post.id for post in posts if post.content[0]=="i"][0]
    
    comments=[Comment(user_id=dan_id,post_id=footy_id,time=datetime.now(),content="boo we should have won your team sucks"),
        Comment(user_id=shelly_id,post_id=footy_id,time=datetime.now(),content="come on you boys in green"),
        Comment(user_id=shelly_id,post_id=nodm_id,time=datetime.now(),content="dm me hun x")]
    [db.session.add(comment) for comment in comments]
    
    comments=Comment.query.all()
    green_id=[comment.id for comment in comments if comment.content[0]=="c"][0]
    boo_id=[comment.id for comment in comments if comment.content[0]=="b"][0]
    
    approvals=[Approval(user_id=shelly_id,ispost=True,post_id=footy_id),
            Approval(user_id=dan_id,ispost=True,post_id=chainmail_id),
            Approval(user_id=kev_id,ispost=False,comment_id=green_id),
            Approval(user_id=dan_id,ispost=False,comment_id=boo_id)]
    [db.session.add(approval) for approval in approvals]
    db.session.commit()