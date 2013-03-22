''' mongoengine data models
'''
from mongoengine import (Document, StringField, DateTimeField, ListField
        , BooleanField)

class Dream(Document):
    ''' the crux of our app - the basic dream instance
    '''
    slug = StringField()
    # user-submitted description of their dream
    description = StringField()
    created = DateTimeField()
    # the extracted keywords
    keywords = ListField(StringField())
    # one clip for each keyword (order should match the keywords attr)
    clips = ListField(StringField())
    # whether or not the video is ready to be played
    montage_incomplete = BooleanField(default=True) # default False is buggy
