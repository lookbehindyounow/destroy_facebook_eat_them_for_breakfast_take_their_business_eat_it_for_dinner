# IMPORTANT - to run you need to createdb games_app; flask db init; flask db migrate; flask db upgrade

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="postgresql://user@localhost:5432/games_app"
db=SQLAlchemy(app)
migrate=Migrate(app,db)

from controllers.games_controller import games_blueprint
from controllers.users_controller import users_blueprint
app.register_blueprint(games_blueprint)
app.register_blueprint(users_blueprint)