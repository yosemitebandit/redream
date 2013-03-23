''' tests.py
checking keyword classification
'''
import unittest

from tasks import _find_keywords

class KeywordExtraction(unittest.TestCase):
    ''' testing keyword discovery
    '''
    def test_fence_jumping(self):
        text = ("I jumped over the fence of my childhood neighbor's backyard"
            ' and there were bright pink, blue and orange snakes. It was very'
            ' frightening and I quickly climbed out.')
        expected_keywords = ['jumped', 'fence', 'childhood', 'neighbor'
            , 'backyard', 'bright', 'pink', 'blue', 'orange', 'snakes'
            , 'frightening', 'climbed']

        # convert to set to account for possible changes in order
        assert set(expected_keywords) == set(_find_keywords(text))
            #, "found keywords: %s" % _find_keywords(text)


    def test_aging_in_the_mirror(self):
        text = ("I had a dream where I was watching myself in the mirror"
            ' and I started to age right in front of my face. My hair turned'
            " white and my face wrinkled. It wasn't scary but it was strange")
        expected_keywords = ['dream', 'watching', 'mirror', 'started', 'age'
            , 'front', 'face', 'hair', 'turned', 'white', 'face'
            , 'wrinkled', 'scary', 'strange']

        assert set(expected_keywords) == set(_find_keywords(text))


    def test_houseboat_party(self):
        text = ('went to a party people were throwing hats like frisbees,'
            ' people were flying up the houseboat stairs')
        expected_keywords = ['party', 'people', 'throwing', 'hats', 'frisbees'
            , 'people', 'flying', 'houseboat', 'stairs']

        assert set(expected_keywords) == set(_find_keywords(text))
