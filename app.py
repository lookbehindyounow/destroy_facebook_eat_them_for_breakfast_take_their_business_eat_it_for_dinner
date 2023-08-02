from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="postgresql://user@localhost:5432/personcatalog"
db=SQLAlchemy(app)
migrate=Migrate(app,db)
from seed import seed
from git_ready import git_ready
app.cli.add_command(seed)
app.cli.add_command(git_ready)

from controllers.posts_controller import posts_blueprint
from controllers.users_controller import users_blueprint
app.register_blueprint(posts_blueprint)
app.register_blueprint(users_blueprint)