''' mongoengine data models
'''
from mongoengine import (Document, StringField, DateTimeField, ListField
        , BooleanField, ReferenceField)

class Dream(Document):
    ''' the crux of our app - the basic dream instance
    '''
    slug = StringField(unique=True)
    # user-submitted description of their dream
    description = StringField()
    created = DateTimeField()
    # the extracted keywords
    keywords = ListField(StringField())
    # one clip for each keyword (order should match the keywords attr)
    clips = ListField(ReferenceField('Clip'))
    # whether or not the video is ready to be played
    montage_incomplete = BooleanField(default=True) # default False is buggy


class Clip(Document):
    mp4_url = StringField()
    source_id = StringField()
    source_title = StringField()
    source_description = StringField()
    source_url = StringField()
    source_owner = StringField()
    source_thumbnail = StringField()
