from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="postgresql://user@localhost:5432/personcatalog" # link to database
db=SQLAlchemy(app)
migrate=Migrate(app,db)
from seed import seed # these 2 lines import the seed function & put it as a terminal command (flask seed)
app.cli.add_command(seed)

from controllers.posts_controller import posts_blueprint # register blueprints with app so controllers work
from controllers.users_controller import users_blueprint
app.register_blueprint(posts_blueprint)
app.register_blueprint(users_blueprint)