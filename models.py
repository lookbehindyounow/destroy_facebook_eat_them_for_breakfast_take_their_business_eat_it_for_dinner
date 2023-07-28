from app import db

class Post(db.Model):
    __tablename__="posts"
    
    id=db.Column(db.Integer,primary_key=True) # look into that uuid(?) thing jack was talking about
    # user_id=db.Column(db.Integer,db.ForeignKey("users.id")) # UNCOMMENT WHEN USERS TABLE EXISTS
    content=db.Column(db.Text())
    
    def __repr__(self):
        return f"<Post {self.id}: {self.first_name} {self.last_name} - born {str(self.dob)}>"

    # posts=db.relationship("Post",backref="user") # LINK FOR USER CLASS WHEN YOU MAKE IT