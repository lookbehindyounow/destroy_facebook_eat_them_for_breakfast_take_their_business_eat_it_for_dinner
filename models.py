from app import db

class User(db.Model):
    __tablename__="users"
    
    id=db.Column(db.Integer,primary_key=True)
    
    name=db.Column(db.String(64))
    password=db.Column(db.String(64))
    
    posts=db.relationship("Post",backref="user")
    comments=db.relationship("Comment",backref="user")
    
    def __repr__(self):
        return f"<User {self.id}: {self.name}>"

class Post(db.Model):
    __tablename__="posts"
    
    id=db.Column(db.Integer,primary_key=True) # look into that uuid(?) thing jack was talking about
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"))
    
    content=db.Column(db.Text())
    
    comments=db.relationship("Comment",backref="post")
    
    def __repr__(self):
        return f"<Post {self.id} by User {self.user_id}: {self.content[:30]}>"
    
    def get_comments(self):
        all_comments=Comment.query.all()
        comments=[[comment,comment.return_name()] for comment in all_comments if comment.post_id==self.id] # inefficient, find sql solution (non-working ideas below)
        # self.comment_count=Comment.query.join(Post).filter(self.id==Comment.post_id)
        # self.comment_count=db.select([comments.columns.id, comments.columns.post_id, comments.columns.content]).where(comments.columns.id==self.id)
        return comments
    
    def count_comments(self):
        return len(self.get_comments())
    
    def return_name(self):
        return User.query.get(self.user_id).name

class Comment(db.Model):
    __tablename__="comments"

    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"))
    post_id=db.Column(db.Integer,db.ForeignKey("posts.id"))
    
    content=db.Column(db.Text())
    
    def __repr__(self):
        return f"<Comment {self.id} by User {self.user_id} on Post {self.post_id}: {self.content[:30]}>"
    
    def return_name(self):
        return User.query.get(self.user_id).name