''' tasks.py
asynch jobs that should be enqueued
'''
import json
from mongoengine import connect
import nltk
import random
import re
import vimeo

from models import Dream

def process_dream(dream_slug, mongo_config, vimeo_config):
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
    clips = [_find_clip(word, vimeo_config) for word in keywords]
    dream.update(set__clips = clips)

    # all done
    # dream.update(set__montage_incomplete = False)


def _find_clip(word, vimeo_config):
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
    # what if no results are available?

    chosen_video = videos[random.randrange(0, len(videos), 1)]
    print chosen_video
    print chosen_video['id']
    print chosen_video['title']



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
