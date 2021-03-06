''' tasks.py
asynch jobs that should be enqueued
'''
import boto
from boto.s3.key import Key as S3_Key
import envoy
import json
from mongoengine import connect
import nltk
from operator import itemgetter
import os
import random
import re
import requests
from redis import Redis
from rq import Queue
from scraper import Scraper
import tempfile
import time
from twitter import *
import vimeo

from models import Dream, Clip
from utilities import generate_random_string

# connect to redis with defaults
queue = Queue(connection=Redis())

def process_dream(dream_slug, configs):
    ''' pull important words from a dream's description
    then find relevant clips for each keyword

    having an annoying issue getting connected to mongo in this file..
    thus the silly passing of the mongo config data
    '''
    # connect to mongo
    connect(configs['mongo']['db_name'], host=configs['mongo']['host']
            , port=int(configs['mongo']['port']))

    dreams = Dream.objects(slug=dream_slug)
    dream = dreams[0]

    keywords = _find_keywords(dream.description)
    groups = _find_keyword_groups(dream.description, keywords)
    # limit to ten keywords and ten groups
    keywords = keywords[0:10]
    keyword_groups = groups[0:10]
    dream.update(set__keywords = keywords)
    dream.update(set__keyword_groups = keyword_groups)

    # preallocate the array of clips
    clips = []
    #for word in keywords:
    for word in keyword_groups:
        new_clip = Clip(
            keyword = word
            , mp4_url = ''
        )
        new_clip.save()
        clips.append(new_clip)
    dream.update(set__clips = clips)

    #for index, word in enumerate(keywords):
    for index, word in enumerate(keyword_groups):
        queue.enqueue_call(
            func=append_clip
            , args=(word, index, dream, clips[index], configs,)
            , timeout=300
        )


def append_clip(word, index, dream, clip, configs):
    ''' appends found clip to a dream
    cleans up the dream's clips at the end of sourcing

    have issues connecting to mongo with this job too..
    '''
    # connect to mongo
    connect(configs['mongo']['db_name'], host=configs['mongo']['host']
            , port=int(configs['mongo']['port']))

    # this function attempts to update the clip object with video data
    while(1):
        find_clip(clip, configs)
        clip.update(inc__mp4_search_attempts=1)
        clip.reload()
        if clip.mp4_url or clip.mp4_search_attempts >= 6:
            break

    # check to see if this was the last keyword to be processed
    # if that's the case, all mp4_url attrs should be a string or None
    dream.reload()
    mp4_urls = [clip.mp4_url for clip in dream.clips]
    for u in mp4_urls:
        print u
    if '' not in mp4_urls:
        # we're done, clean up the array by removing None values
        clips = [c for c in dream.clips if c.mp4_url]
        dream.update(set__clips = clips)
        dream.update(set__montage_incomplete = False)

        # send to the twitterverse
        t = Twitter(auth=OAuth(
            configs['twitter']['access_token']
            , configs['twitter']['access_token_secret']
            , configs['twitter']['consumer_key']
            , configs['twitter']['consumer_secret'])
        )

        url = 'http://redream.us/%s' % dream.slug

        # tweet @ someone
        if dream.twitter_handles:
            handles = ', '.join(dream.twitter_handles[0:3])
            note = 'your dream is ready: '
            status = '%s %s %s' % (handles, note, url)

        # just tweet to the public timeline
        else:
            # would ideally break the description on different words
            prefix = dream.description[0:100].strip()
            status = '%s.. %s' % (prefix, url)

        t.statuses.update(status=status)

    print('')
    print('')


def find_clip(clip, configs):
    ''' find a relevant archival video based on the word's search term
    '''
    # login to vimeo
    client = vimeo.Client(key=configs['vimeo']['consumer_key']
        , secret = configs['vimeo']['consumer_secret']
        , callback = configs['vimeo']['callback_url'])

    # sorting categories; note that 'newest' seemed spammy
    sorting = random.choice(['oldest', 'relevant', 'most_played'
        , 'most_commented', 'most_liked', 'oldest', 'oldest', 'oldest'])

    try:
        # may fail if certain unicode chars come back from vimeo
        # \u2019 (right quotation mark), for instance
        result = json.loads(client.get(
                    'vimeo.videos.search'
                    , query=clip.keyword
                    , page=1
                    , per_page=50
                    , full_response=1
                    , sort=sorting
                ))
    except:
        print ' skipping; vimeo search exception'
        clip.update(set__mp4_url = None)
        return None

    videos = result['videos']['video']
    if not videos:
        print ' skipping; no videos for "%s" in "%s" search' % (clip.keyword
                , sorting)
        clip.update(set__mp4_url = None)
        return None

    # select a video with a short but at least 3 second duration
    durations = [int(v['duration']) for v in videos if int(v['duration']) >= 3]
    if len(durations) > 5:
        durations.sort()
        durations = durations[0:5]

    selected_duration = durations[random.choice(range(0, len(durations)))]

    for v in videos:
        if int(v['duration']) == selected_duration:
            video = v
            break
    print '  %s with sorting "%s" --> vimeo.com/%s' % (clip.keyword, sorting
        , video['id'])

    # pull the vimeo mp4
    vimeo_mp4_url = Scraper.get_vimeo(video['id'])
    if not vimeo_mp4_url:
        print ' skipping; scraper was unable to retrieve an mp4'
        clip.update(set__mp4_url = None)
        return None

    # download the file
    print 'downloading local copy'
    r = requests.get(vimeo_mp4_url)
    tmp_path = '%s/redream-%s.mp4' % (tempfile.gettempdir()
            , generate_random_string(10))
    with open(tmp_path, 'wb') as video_file:
        video_file.write(r.content)

    if int(video['duration']) > 20:
        # crop the video - start at 20-70% and take 5-15% of total
        print 'cropping with ffmpeg'
        start_fraction = (random.random()*(0.7-0.2)) + 0.2
        start = time.strftime('%H:%M:%S'
                , time.gmtime(int(video['duration'])*start_fraction))
        length_fraction = (random.random()*(0.15-0.05)) + 0.05
        length = time.strftime('%H:%M:%S'
                , time.gmtime(int(video['duration'])*length_fraction))
        out_path = '%s/redream-%s.mp4' % (tempfile.gettempdir()
                , generate_random_string(10))
        # envoy command from http://askubuntu.com/a/35645/68373
        try:
            envoy.run('ffmpeg -acodec copy -vcodec copy -ss %s -t %s -i %s %s'
                    % (start, length, tmp_path, out_path))
        except AttributeError:
            print 'skipping; ffmpeg attr error (bad save path?)'
            return None
    else:
        # short source vid, don't crop
        out_path = tmp_path

    # rehost the file on s3
    print 'moving to s3'
    connection = boto.connect_s3(
        aws_access_key_id=configs['aws']['access_key_id']
        , aws_secret_access_key=configs['aws']['secret_access_key'])

    # create bucket if it doesn't exist
    if not connection.lookup(configs['aws']['s3_bucket']):
        bucket = connection.create_bucket(configs['aws']['s3_bucket'])
    else:
        bucket = connection.get_bucket(configs['aws']['s3_bucket'])

    s3_key = S3_Key(bucket)
    s3_key.key = '%s.mp4' % generate_random_string(30)
    s3_key.set_contents_from_filename(out_path)
    s3_key.make_public()

    s3_url = 'http://s3.amazonaws.com/%s/%s' % (configs['aws']['s3_bucket']
        , s3_key.key)

    # delete local copies
    os.unlink(tmp_path)
    if out_path != tmp_path:
        os.unlink(out_path)

    # save into db
    print 'saving to db'
    clip.update(set__mp4_url = s3_url)
    clip.update(set__archive_name = 'vimeo')
    clip.update(set__source_id = video['id'])
    clip.update(set__source_title = video['title'])
    clip.update(set__source_description = video['description'])
    clip.update(set__source_url = video['urls']['url'][0]['_content'])
    clip.update(set__source_owner = video['owner']['username'])
    clip.update(set__source_thumbnail_url = 
            video['thumbnails']['thumbnail'][0]['_content'])

    return True


def _find_keyword_groups(text, keywords):
    ''' group relevant keywords together
    '''
    tokens = nltk.word_tokenize(text)
    # strip punctuation from the tokens
    punct = re.compile(r'[-.?!,";()]')
    tokens = [punct.sub('', t) for t in tokens if punct.sub('', t)]

    # group together consecutive keywords
    groups = []
    group = []
    while(tokens):
        word = tokens.pop(0)
        if word in keywords:
            group.append(word)
        elif word not in keywords and group:
            groups.append('+'.join(group))
            group = []
    else:
        # catch the last group if it's not an empty string
        if group:
            groups.append('+'.join(group))

    return groups


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
