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

        configs = {
            'mongo': mongo_config
            , 'vimeo': app.config['VIMEO']
            , 'aws': app.config['AWS']
            , 'twitter': app.config['TWITTER']
        }
        queue.enqueue_call(func=process_dream
            , args=(new_dream.slug, configs,)
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
    # +1 to account for the fact that we have keywords
    response['percentage'] = round(
            float(len(mp4_urls)+1) / (len(dream.keywords)+1), 2)
    return jsonify(response)


@app.route('/<dream_slug>/twitter')
def twitter_handle(dream_slug):
    ''' POST a twitter handle here
    and we'll tweet @ them when the video's ready
    '''
    response = {'success': False, 'message': ''}

    handle = request.form.get('handle', '')
    if not handle:
        response['message'] = 'no handle specified'
        return jsonify(response)

    # add the '@' prefix
    if handle[0] != '@':
        handle = '@' + handle

    # validate the handle
    r = re.compile(r'(^|[^@\w])@(\w{1,15})\b')
    if not r.match(handle):
        response['message'] = 'invalid handle'
        return jsonify(response)

    # pull the dream from the db
    dreams = Dream.objects(slug=dream_slug)
    if not dreams:
        # dream not found! ..maybe have a 404 page
        abort(404)
    dream = dreams[0]

    # push in the handle
    dream.update(push__twitter_handles=handle)


if __name__ == '__main__':
    app.run(
        host = app.config['HOST']
        , port = int(app.config['PORT'])
    )
