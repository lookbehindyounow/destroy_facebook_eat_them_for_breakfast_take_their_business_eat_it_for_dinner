from app import db

class User(db.Model):
    __tablename__="users"
    
    id=db.Column(db.Integer,primary_key=True)
    first_name=db.Column(db.String(64))
    last_name=db.Column(db.String(64))
    dob=db.Column(db.Date)
    games=db.relationship("Game",backref="user")
    
    def __repr__(self):
        return f"<User {self.id}: {self.first_name} {self.last_name} - born {str(self.dob)}>"

class Game(db.Model):
    __tablename__="games"
    
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(64))
    genre=db.Column(db.String(64))
    description=db.Column(db.Text())
    age_rating=db.Column(db.Integer)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"))
    
    def __repr__(self):
        return f"<Game {self.id}: {self.title} - rated {self.age_rating}>"
    
    def check_in(self):
        self.user_id=None
    
    def check_out(self,user_id):
        self.user_id=user_id