''' config file for the redream app
copy this somewhere safe and set an env var:
    $ export REDREAM_SETTINGS=/path/to/settings/file
'''

DEBUG = False

HOST = '0.0.0.0'
PORT = 4003

# generate a real secret key with os.urandom(24)
SECRET_KEY = 'keep it secret, keep it safe'
