from app import db
from models import Post, Comment
import click
from flask.cli import with_appcontext

@click.command(name='seed')
@with_appcontext
def seed():
    Post.query.delete()
    Comment.query.delete()
    
    posts=[Post(content="come on football yass 3 nil"),
           Post(content="nobody dm goin thru it"),
           Post(content="if you do not share this post your mother will die in her sleep tonight there used to be a little girl who was scared of the dark she did not retweet this message & then later that night in her room there was a presence at the end of her bed she was never heard from again I do not give personcatalog permission to use my data or my photos COPY & PASTE THI S MESSAGE IT LEGAL BONDAGE CONTRACT IT WORKS NO REALLY")
    ]
    [db.session.add(post) for post in posts]
    db.session.commit()
    
    posts=Post.query.all()
    footy_id=[post.id for post in posts if post.content[0]=="c"][0]
    
    comments=[Comment(post_id=footy_id,content="boo we should have won your team sucks"),
              Comment(post_id=footy_id,content="come on you boys in green")
    ]
    [db.session.add(comment) for comment in comments]
    db.session.commit()