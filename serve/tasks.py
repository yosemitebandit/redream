''' tasks.py
asynch jobs that should be enqueued
'''
import nltk
import re

def process_dream(dream):
    ''' pull important words from a dream's description
    then find relevant clips for each keyword
    '''
    keywords = _find_keywords(dream.description)
    dream.update(set__keywords = keywords)


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
