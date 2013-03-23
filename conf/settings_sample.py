''' config file for the redream app
copy this somewhere safe and set an env var:
    $ export REDREAM_SETTINGS=/path/to/settings/file
'''

DEBUG = False

HOST = '0.0.0.0'
PORT = 4003

# generate a real secret key with os.urandom(24)
SECRET_KEY = 'keep it secret, keep it safe'

MONGO = {
    'db_name': 'redream'
    , 'host': 'localhost'
    , 'port': 27017
}

AWS = {
    's3_bucket': 'your-redream-bucket-name'
    , 'access_key_id': 'AKzyxw987'
    , 'secret_access_key': 'lmnop456'
}

VIMEO = {
    'consumer_key': 'qrstuv'
    , 'consumer_secret': '321abc'
    , 'callback_url': ''
}

TWITTER = {
    'access_token': '54231'
    , 'access_token_secret': '321abc'
    , 'consumer_key': 'zyxwv'
    , 'consumer_secret': 'lmnop'
}

GOOGLE_ANALYTICS = {
    'code': 'UA-123-1'
    , 'url': 'redreameroo.com'
}
