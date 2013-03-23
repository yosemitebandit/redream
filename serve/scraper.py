import sys
import re
import requests

class Scraper (object):
    @staticmethod
    def get_vimeo (id):
        # print 'id: ', id
        r = requests.get('http://vimeo.com/' + id)
        if r.status_code != 200:
            return None
        matcher = re.compile('document\.getElementById\(\'player_(.+)\n', re.IGNORECASE)
        scriptblock = matcher.search(r.text)
        if scriptblock is None:
            return None
        matcher = re.compile('"timestamp":([0-9]+)', re.IGNORECASE)
        timestamp = matcher.search(scriptblock.group())
        matcher = re.compile('"signature":"([a-z0-9]+)"', re.IGNORECASE)
        signature = matcher.search(scriptblock.group())
        # print [timestamp.group(1), signature.group(1)]

        url = 'http://player.vimeo.com/play_redirect?clip_id=' + id + '&sig=' + signature.group(1)  + '&time=' + timestamp.group(1) + '&quality=sd'

        r2 = requests.get(url, allow_redirects=False)
        return r2.headers['location']

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print Scraper.get_vimeo(sys.argv[1])

