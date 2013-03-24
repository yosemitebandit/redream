''' mongoengine data models
'''
from mongoengine import (Document, StringField, DateTimeField, ListField
        , BooleanField, ReferenceField, IntField)

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
    # tweet at these folks once the video is ready
    twitter_handles = ListField(StringField())


class Clip(Document):
    keyword = StringField()
    mp4_url = StringField()
    archive_name = StringField()  # vimeo, archive.org..
    source_id = StringField()
    source_title = StringField()
    source_description = StringField()
    source_url = StringField()
    source_owner = StringField()
    source_thumbnail_url = StringField()
    mp4_search_attempts = IntField(default=0)
