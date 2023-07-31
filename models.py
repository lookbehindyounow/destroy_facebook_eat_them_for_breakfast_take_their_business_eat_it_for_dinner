from app import db
from datetime import datetime

class User(db.Model):
    __tablename__="users"
    
    id=db.Column(db.Integer,primary_key=True)
    
    name=db.Column(db.String(64))
    password=db.Column(db.String(64))
    
    posts=db.relationship("Post",backref="user")
    comments=db.relationship("Comment",backref="user")
    approvals=db.relationship("Approval",backref="user")
    
    def __repr__(self):
        return f"<User {self.id}: {self.name}>"

class PostOrComment():
    id=db.Column(db.Integer,primary_key=True) # look into that uuid(?) thing jack was talking about
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"))
    time=db.Column(db.DateTime)
    
    content=db.Column(db.Text())
    
    def set_variables(self):
        self.name=User.query.get(self.user_id).name
        
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
        
        all_approvals=Approval.query.all() # see class below - needs changed
        if type(self)==Post:
            self.approvals=[approval for approval in all_approvals if approval.ispost and approval.post_id==self.id]
        else:
            self.approvals=[approval for approval in all_approvals if not approval.ispost and approval.comment_id==self.id]
        
        return self


class Post(PostOrComment,db.Model):
    __tablename__="posts"
    
    comments=db.relationship("Comment",backref="post")
    approvals=db.relationship("Approval",backref="post")
    
    def __repr__(self):
        return f"<Post {self.id} by User {self.user_id}: {self.content[:30]}>"
    
    def get_comments(self):
        all_comments=Comment.query.all() # inefficient, find sql solution (non-working ideas below)
        comments=[comment.set_variables() for comment in all_comments if comment.post_id==self.id]
        # self.comment_count=Comment.query.join(Post).filter(self.id==Comment.post_id)
        # self.comment_count=db.select([comments.columns.id, comments.columns.post_id, comments.columns.content]).where(comments.columns.id==self.id)
        self.comment_count=len(comments)
        return comments

class Comment(PostOrComment,db.Model):
    __tablename__="comments"
    
    post_id=db.Column(db.Integer,db.ForeignKey("posts.id"))
    
    approvals=db.relationship("Approval",backref="comment")
    
    def __repr__(self):
        return f"<Comment {self.id} by User {self.user_id} on Post {self.post_id}: {self.content[:30]}>"

class Approval(db.Model):
    __tablename__="approvals"
    
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"))
    
    ispost=db.Column(db.Boolean)
    post_id=db.Column(db.Integer,db.ForeignKey("posts.id"))
    comment_id=db.Column(db.Integer,db.ForeignKey("comments.id"))