''' serve.py
simple flask server
'''
from flask import Flask, request, abort, render_template

app = Flask(__name__)
app.config.from_envvar('REDREAM_SETTINGS')


@app.route('/')
def home():
    ''' show the homepage
    '''
    return 'hullo!'


if __name__ == '__main__':
    app.run(
        host = app.config['HOST']
        , port = int(app.config['PORT'])
    )
