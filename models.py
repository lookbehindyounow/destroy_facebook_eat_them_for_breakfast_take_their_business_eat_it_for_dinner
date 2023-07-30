from app import db
from datetime import datetime

class User(db.Model):
    __tablename__="users"
    
    id=db.Column(db.Integer,primary_key=True)
    
    name=db.Column(db.String(64))
    password=db.Column(db.String(64))
    
    posts=db.relationship("Post",backref="user")
    comments=db.relationship("Comment",backref="user")
    
    def __repr__(self):
        return f"<User {self.id}: {self.name}>"

class PostOrComment():
    def set_name(self):
        self.name=User.query.get(self.user_id).name
    
    def find_time(self):
        seconds_since=(datetime.now()-self.time).seconds
        if seconds_since<86400:
            if seconds_since<3600:
                if seconds_since<60:
                    self.when="just now"
                else:
                    self.when=str(seconds_since//60)+" min ago" # (s) calc?
            else:
                self.when=str(seconds_since//3600)+" hr ago"
        else:
            self.when=(str(self.time)[8:10]+"/"+str(self.time)[5:7]+"/"+str(self.time)[2:4]
                        +" - "+str(self.time)[11:13]+":"+str(self.time)[14:16])

class Post(PostOrComment,db.Model):
    __tablename__="posts"
    id=db.Column(db.Integer,primary_key=True) # look into that uuid(?) thing jack was talking about
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"))
    time=db.Column(db.DateTime)
    
    content=db.Column(db.Text())
    
    comments=db.relationship("Comment",backref="post")
    
    def __repr__(self):
        return f"<Post {self.id} by User {self.user_id}: {self.content[:30]}>"
    
    def get_comments(self):
        all_comments=Comment.query.all() # inefficient, find sql solution (non-working ideas below)
        comments=[]
        for comment in all_comments:
            if comment.post_id==self.id:
                comment.set_name()
                comments.append(comment)
        # self.comment_count=Comment.query.join(Post).filter(self.id==Comment.post_id)
        # self.comment_count=db.select([comments.columns.id, comments.columns.post_id, comments.columns.content]).where(comments.columns.id==self.id)
        return comments
    
    def count_comments(self):
        self.comment_count=len(self.get_comments())

class Comment(PostOrComment,db.Model):
    __tablename__="comments"
    id=db.Column(db.Integer,primary_key=True) # look into that uuid(?) thing jack was talking about
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"))
    time=db.Column(db.DateTime)
    
    content=db.Column(db.Text())
    
    post_id=db.Column(db.Integer,db.ForeignKey("posts.id"))
    
    def __repr__(self):
        return f"<Comment {self.id} by User {self.user_id} on Post {self.post_id}: {self.content[:30]}>"