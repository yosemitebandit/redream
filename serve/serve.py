''' serve.py
simple flask server
'''
import datetime
from flask import (Flask, request, abort, render_template, redirect, url_for
    , jsonify)
from mongoengine import connect
from redis import Redis
from rq import Queue

from models import Dream
from utilities import generate_random_string
from tasks import process_dream

# initiate the webapp
app = Flask(__name__)
app.config.from_envvar('REDREAM_SETTINGS')

# connect to mongo
mongo_config = app.config['MONGO']
connect(mongo_config['db_name'], host=mongo_config['host']
        , port=int(mongo_config['port']))

# connect to redis with defaults
queue = Queue(connection=Redis())

# pull the vimeo and aws config data
vimeo_config = app.config['VIMEO']
aws_config = app.config['AWS']


@app.route('/', methods=['GET', 'POST'])
def home():
    ''' GET to view the dream-input controls
    POST to create a new dream-tage
    '''
    if request.method == 'GET':
        return render_template('home.html')

    if request.method == 'POST':
        # check CSRF token..

        # save a new dream instance in the db
        new_dream = Dream(
            # might want to do something to insure uniqueness
            slug = generate_random_string(5)
            , description = request.form.get('description', '')
            , created = datetime.datetime.utcnow()
        )
        new_dream.save()

        # enqueue the processing for keyword extraction and sourcing clips
        queue.enqueue_call(func=process_dream
            , args=(new_dream.slug, mongo_config, vimeo_config, aws_config,)
            , timeout=600)

        # redirect to the invidiual dream page
        return redirect(url_for('dream', dream_slug = new_dream.slug))


@app.route('/<dream_slug>')
def dream(dream_slug):
    ''' GET to find a certain dream-tage
    '''
    # pull the dream from the db
    dreams = Dream.objects(slug=dream_slug)
    if not dreams:
        # dream not found! ..maybe have a 404 page
        return redirect(url_for('home'))

    return render_template('dream.html', dream=dreams[0])


@app.route('/<dream_slug>/progress')
def render_progress(dream_slug):
    ''' GET to see how many video clips we've amassed
    '''
    # pull the dream from the db
    dreams = Dream.objects(slug=dream_slug)
    if not dreams:
        # dream not found! ..maybe have a 404 page
        abort(404)
    dream = dreams[0]

    response = {'percentage': 0, 'success': True}
    if not dream.keywords:
        return jsonify(response)

    mp4_urls = ['tally' for c in dream.clips if c.mp4_url != '']
    response['percentage'] = round(float(len(mp4_urls)) / len(dream.keywords), 2)
    return jsonify(response)


if __name__ == '__main__':
    app.run(
        host = app.config['HOST']
        , port = int(app.config['PORT'])
    )
