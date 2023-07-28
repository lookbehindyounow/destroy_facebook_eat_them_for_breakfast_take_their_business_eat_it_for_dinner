# PersonCatalog
## an original idea for a completely unique social network like none other
##### you can make posts... and comments

IMPORTANT - to run you will need python3, postgresql, flask, flask_sqlalchemy & flask_migrate.
Once you have all these, clone the repository, cd into the folder containing everything & enter the following commands:
createdb personcatalog
flask db init
flask db migrate
flask db upgrade
flask seed
flask run

After you've done this open your web browser & go to 127.0.0.1:5000, if it doesn't work you may need to change the port to 4999. Go into the file called .flaskenv & add a line that says FLASK_RUN_PORT=4999, then try again in the browser at 127.0.0.1:4999