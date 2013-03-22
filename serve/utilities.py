''' utilities.py
spurious useful functions
'''
import os

def generate_random_string(length):
    ''' for generating slugs
    '''
    # technique from: http://stackoverflow.com/questions/2898685
    corpus = 'abcdefghjkmnpqrstwxyz'
    return ''.join(
        map(lambda x: corpus[ord(x)%len(corpus)], os.urandom(length)))
