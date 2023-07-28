from app import db

    # posts=db.relationship("Post",backref="user") # LINK FOR USER CLASS WHEN YOU MAKE IT

class Post(db.Model):
    __tablename__="posts"
    
    id=db.Column(db.Integer,primary_key=True) # look into that uuid(?) thing jack was talking about
    # user_id=db.Column(db.Integer,db.ForeignKey("users.id")) # UNCOMMENT WHEN USERS TABLE EXISTS
    
    content=db.Column(db.Text())
    
    comments=db.relationship("Comment",backref="post")
    
    def __repr__(self):
        return f"<Post {self.id}: {self.content[:30]}>"

class Comment(db.Model):
    __tablename__="comments"

    id=db.Column(db.Integer,primary_key=True)
    # user_id=db.Column(db.Integer,db.ForeignKey("users.id")) # UNCOMMENT WHEN USERS TABLE EXISTS
    post_id=db.Column(db.Integer,db.ForeignKey("posts.id"))
    
    content=db.Column(db.Text())
    
    def __repr__(self):
        return f"<Comment {self.id} on Post {self.post_id}: {self.content[:30]}>"