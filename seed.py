from app import db
from models import User, Post, Comment
import click
from flask.cli import with_appcontext

@click.command(name='seed')
@with_appcontext
def seed():
    Comment.query.delete()
    Post.query.delete()
    User.query.delete()
    
    users=[User(name="kev",password="kev123"),
        User(name="dan",password="password"),
        User(name="shelly",password="meow")
    ]
    [db.session.add(user) for user in users]
    db.session.commit()
    
    users=User.query.all()
    kev_id=[user.id for user in users if user.name=="kev"][0]
    dan_id=[user.id for user in users if user.name=="dan"][0]
    shelly_id=[user.id for user in users if user.name=="shelly"][0]
    
    posts=[Post(user_id=kev_id,content="come on football yass 3 nil"),
        Post(user_id=dan_id,content="nobody dm goin thru it"),
        Post(user_id=shelly_id,content="if you do not share this post your mother will die in her sleep tonight there used to be a little girl who was scared of the dark she did not retweet this message & then later that night in her room there was a presence at the end of her bed she was never heard from again I do not give personcatalog permission to use my data or my photos COPY & PASTE THI S MESSAGE IT LEGAL BONDAGE CONTRACT IT WORKS NO REALLY")
    ]
    [db.session.add(post) for post in posts]
    db.session.commit()
    
    posts=Post.query.all()
    footy_id=[post.id for post in posts if post.content[0]=="c"][0]
    nodm_id=[post.id for post in posts if post.content[0]=="n"][0]
    
    comments=[Comment(user_id=dan_id,post_id=footy_id,content="boo we should have won your team sucks"),
        Comment(user_id=shelly_id,post_id=footy_id,content="come on you boys in green"),
        Comment(user_id=shelly_id,post_id=nodm_id,content="dm me hun x")
    ]
    [db.session.add(comment) for comment in comments]
    db.session.commit()