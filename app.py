# IMPORTANT - to run you need to open a terminal & type the commands:
# createdb personcatalog
# flask db init
# flask db migrate
# flask db upgrade

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="postgresql://user@localhost:5432/personcatalog"
db=SQLAlchemy(app)
migrate=Migrate(app,db)

from controllers.posts_controller import posts_blueprint
app.register_blueprint(posts_blueprint)