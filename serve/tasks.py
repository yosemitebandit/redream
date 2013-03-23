''' tasks.py
asynch jobs that should be enqueued
'''
import boto
from boto.s3.key import Key as S3_Key
import json
from mongoengine import connect
import nltk
import random
import re
import requests
from scraper import Scraper
import vimeo

from models import Dream, Clip
from utilities import generate_random_string

def process_dream(dream_slug, mongo_config, vimeo_config, aws_config):
    ''' pull important words from a dream's description
    then find relevant clips for each keyword

    having an annoying issue getting connected to mongo in this file..
    thus the silly passing of the mongo config data
    '''
    # connect to mongo
    connect(mongo_config['db_name'], host=mongo_config['host']
            , port=int(mongo_config['port']))

    dreams = Dream.objects(slug=dream_slug)
    dream = dreams[0]

    keywords = _find_keywords(dream.description)
    dream.update(set__keywords = keywords)

    # this should be paralellized via separate jobs or another method..
    clips = [_find_clip(word, vimeo_config, aws_config) for word in keywords]
    dream.update(set__clips = clips)

    # all done
    dream.update(set__montage_incomplete = False)


def _find_clip(word, vimeo_config, aws_config):
    # find a relevant archival video based on the word's search term
    # login to vimeo
    client = vimeo.Client(key=vimeo_config['consumer_key']
        , secret = vimeo_config['consumer_secret']
        , callback = vimeo_config['callback_url'])

    result = json.loads(client.get(
                'vimeo.videos.search'
                , query=word
                , page=1
                , per_page=5
                , full_response=1
            ))
    videos = result['videos']['video']
    video = videos[random.randrange(0, len(videos), 1)]
    # what if no results are available?

    # pull the vimeo mp4
    vimeo_mp4_url = Scraper.get_vimeo(video['id'])

    # download the file
    print 'downloading local copy'
    r = requests.get(vimeo_mp4_url)
    tmp_path = '/tmp/redream-%s.mp4' % generate_random_string(10)
    with open(tmp_path, 'wb') as video_file:
        video_file.write(r.content)

    # rehost the file on s3
    print 'moving to s3'
    connection = boto.connect_s3(
        aws_access_key_id=aws_config['access_key_id']
        , aws_secret_access_key=aws_config['secret_access_key'])
    bucket = connection.create_bucket(aws_config['s3_bucket'])

    s3_key = S3_Key(bucket)
    s3_key.key = '%s.mp4' % generate_random_string(30)
    s3_key.set_contents_from_filename(tmp_path)
    s3_key.make_public()

    s3_url = 'https://s3.amazonaws.com/%s/%s' % (aws_config['s3_bucket']
        , s3_key.key)

    # delete local copy
    #os.unlink(tmp_path)

    # save into db
    print 'saving to db'
    new_clip = Clip(
        mp4_url = s3_url
        , archive_name = 'vimeo'
        , source_id = video['id']
        , source_title = video['title']
        , source_description = video['description']
        , source_url = video['urls']['url'][0]['_content']
        , source_owner = video['owner']['username']
        , source_thumbnail_url = (
            video['thumbnails']['thumbnail'][0]['_content'])
    )
    new_clip.save()

    return new_clip


def _find_keywords(text):
    # tokenize and classify with nltk
    # returns list of sets: [('I', 'PRP'), ('jumped', 'VBD')]
    text = nltk.pos_tag(nltk.word_tokenize(text))

    # the classifications we're interested in keeping:
    selected_tags = [
        'ADJ', 'JJ', 'JJS', 'JJR'  # adjective
        , 'FW'  # foreign word
        , 'N', 'NN', 'NS', 'NNS'  # noun and nouns
        , 'NP', 'NNP', 'NPS', 'NNPS'  # proper noun
        , 'NUM'  # number
        , 'UH'  # interjection (oops, umph)
        , 'V', 'VB'  # verb
        , 'VBP'  # verb singular (take)
        , 'VBZ'  # verb third person singular (takes)
        , 'VD', 'VBD'  # past tense (made, asked)
        , 'VG', 'VBG'  # present participle (playing, working)
        , 'VN', 'VBN'  # past participle (given, taken)
    ]

    past_tense_verbs = ['VD', 'VBD', 'VN', 'VBN']

    # keep words that are classified like we want
    keywords = []
    for word in text:
        # each "word" is something like ('jumped', 'VBD')
        if word[1] in selected_tags:
            # filter out short past tense verbs
            if word[1] in past_tense_verbs and len(word[0]) <= 4:
                continue
            # filter out short words
            if len(word[0]) <= 2:
                continue

            # save words that remain
            keywords.append(word[0])

    # strip punctuation and special chars from the resulting keywords
    punctuation = re.compile(r'[-.?!,";()]')
    keywords = [punctuation.sub('', kw) for kw in keywords]

    return keywords
