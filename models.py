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
    
    def get_comments(self):
        all_comments=Comment.query.all()
        comments=[comment for comment in all_comments if comment.post_id==self.id] # inefficient, find sql solution (non-working ideas below)
        # self.comment_count=Comment.query.join(Post).filter(self.id==Comment.post_id)
        # self.comment_count=db.select([comments.columns.id, comments.columns.post_id, comments.columns.content]).where(comments.columns.id==self.id)
        return comments
    
    def count_comments(self):
        return len(self.get_comments())

class Comment(db.Model):
    __tablename__="comments"

    id=db.Column(db.Integer,primary_key=True)
    # user_id=db.Column(db.Integer,db.ForeignKey("users.id")) # UNCOMMENT WHEN USERS TABLE EXISTS
    post_id=db.Column(db.Integer,db.ForeignKey("posts.id"))
    
    content=db.Column(db.Text())
    
    def __repr__(self):
        return f"<Comment {self.id} on Post {self.post_id}: {self.content[:30]}>"