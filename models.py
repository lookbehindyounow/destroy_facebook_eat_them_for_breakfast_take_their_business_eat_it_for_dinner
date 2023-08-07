from app import db
from datetime import datetime

class Roulette: # will need to store some starting variables for roulette,
    def __init__(self): # I reckon a roulette object stored as an attribute with each user is a neat idea 
        self.wheel=False
        self.ball=False

class User(db.Model):
    __tablename__="users" # class name is User but table should be called users not user
    
    id=db.Column(db.Integer,primary_key=True)
    
    name=db.Column(db.String(64))
    password=db.Column(db.String(64))
    
    # text field is ideal for base64, which is how the profile pictures are encoded in the database
    pfp=db.Column(db.Text())
    
    roulette=Roulette() # creates roulette object for each user
    
    friends=db.relationship("Friend",backref="user") # linking the one to all of it's manys
    friendships=db.relationship("Friendship",backref="user")
    posts=db.relationship("Post",backref="user")
    comments=db.relationship("Comment",backref="user")
    approvals=db.relationship("Approval",backref="user")
    
    def __repr__(self): # changes what shows up if you try to print an object to terminal
        return f"<User {self.id}: {self.name}>"

class Friend(db.Model):
    # This is dummy table that holds only a copy of every user's id so we can spoof a many to many
    # relationship between the users table & itself
    __tablename__="friends"
    
    id=db.Column(db.Integer,db.ForeignKey("users.id"),primary_key=True) # primary & foreign key, spooky
    
    friendships=db.relationship("Friendship",backref="friend")
    
    def __repr__(self):
        return f"<Friend {self.id} (same id as corresponding User)>"

class Friendship(db.Model):
    __tablename__="friendships"
    
    id=db.Column(db.Integer,primary_key=True)
    
    # it wouldn't let me have two foreign keys for the same table, hence the need for the friends table^^
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"))
    friend_id=db.Column(db.Integer,db.ForeignKey("friends.id"))
    
    def __repr__(self):
        return f"<Friendship {self.id} between Users {self.user_id} & {self.friend_id}>"

class PostOrComment(): # posts & comments share a lot of attributes & methods so they both inherit from here
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"))
    time=db.Column(db.DateTime)
    
    content=db.Column(db.Text())
    
    def set_variables(self):
        # this method gathers data about a post or comment from records linked to it,
        # as these variables can change without the post or comment's record changing
        user=User.query.get(self.user_id) # get poster's name & pfp
        self.name=user.name
        self.pfp=user.pfp
        
        # find out how long since posted
        seconds_since=(datetime.now()-self.time).seconds
        if seconds_since<86400:
            if seconds_since<3600:
                if seconds_since<60:
                    self.when="just now"
                else:
                    self.when=str(seconds_since//60)+" mins ago"
            else:
                self.when=str(seconds_since//3600)+" hrs ago"
            if self.when[:2]=="1 ":
                self.when=self.when[:-5]+self.when[-4:]
        else: # or just say the date & time if longer than a day
            self.when=(str(self.time)[8:10]+"/"+str(self.time)[5:7]+"/"+str(self.time)[2:4]
                        +" - "+str(self.time)[11:13]+":"+str(self.time)[14:16])
        
        if type(self)==Post:
            self.approvals=Approval.query.filter_by(ispost=True,post_id=self.id).all()
            self.get_comments() # if it's a post, repeat this process for all it's comments
        else:
            self.approvals=Approval.query.filter_by(ispost=False,comment_id=self.id).all()
    
    def edit(self,content,public=None):
        self.content=content
        self.public=public
        db.session.commit()

class Post(PostOrComment,db.Model):
    __tablename__="posts"
    
    public=db.Column(db.Boolean)
    
    comments=db.relationship("Comment",backref="post")
    approvals=db.relationship("Approval",backref="post")
    
    def __repr__(self):
        return f"<Post {self.id} by User {self.user_id}: {self.content[:30]}>"
    
    def get_comments(self):
        self.comments=Comment.query.filter_by(post_id=self.id).order_by(Comment.time).all()
        # here's the other end of that slightly recursive thing at the end of set_variables()
        [comment.set_variables() for comment in self.comments]

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
    
    ispost=db.Column(db.Boolean) # tells us whether an approval is registered to a post or comment
    post_id=db.Column(db.Integer,db.ForeignKey("posts.id"))
    comment_id=db.Column(db.Integer,db.ForeignKey("comments.id"))
    
    def __repr__(self):
        message=f"<Approval {self.id} by User {self.user_id} on >"
        if self.ispost:
            message=message+f"Post {self.post_id}"
        else:
            message=message+f"Comment {self.comment_id}"
        return message