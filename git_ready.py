import click, os
from flask.cli import with_appcontext

@click.command(name='git_ready')
@with_appcontext
def git_ready():
    [os.unlink(os.getcwd()+"/static/pfp/"+filename) for filename in os.listdir(os.getcwd()+"/static/pfp/")]
    open(os.getcwd()+"/static/pfp/dummy_file_for_git.whatever",'w').close()