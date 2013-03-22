''' serve.py
simple flask server
'''
from flask import Flask, request, abort, render_template, redirect, url_for
from mongoengine import connect

# initiate the webapp
app = Flask(__name__)
app.config.from_envvar('REDREAM_SETTINGS')

# connect to the db
mongo_config = app.config['MONGO']
connect(mongo_config['db_name'], host=mongo_config['host']
        , port=int(mongo_config['port']))


@app.route('/', methods=['GET', 'POST'])
def home():
    ''' GET to view the dream-input controls
    POST to create a new dream-tage
    '''
    if request.method == 'GET':
        return render_template('home.html')

    if request.method == 'POST':
        # make a new dream instance in the db
        # initiate the workers for processing the description
        # redirect to the invidiual dream page
        return redirect(url_for('dream', dream_slug = dream.slug))


@app.route('/<dream_slug>')
def dream(dream_slug):
    ''' GET to find a certain dream-tage
    '''
    # pull the dream from the db
    return render_template('dream.html', dream=dream)


if __name__ == '__main__':
    app.run(
        host = app.config['HOST']
        , port = int(app.config['PORT'])
    )
