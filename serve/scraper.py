import sys
import re
import requests

class Scraper (object):
    @staticmethod
    def get_vimeo (id):
        headers = {
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3)'
                ' AppleWebKit/536.28.10 (KHTML, like Gecko) Version/6.0.3'
                ' Safari/536.28.10')
        }
        # print 'id: ', id
        r = requests.get('http://vimeo.com/' + id, headers=headers)
        if r.status_code != 200:
            return None
        matcher = re.compile('document\.getElementById\(\'player_(.+)\n'
                , re.IGNORECASE)
        scriptblock = matcher.search(r.text)
        if scriptblock is None:
            return None
        matcher = re.compile('"timestamp":([0-9]+)', re.IGNORECASE)
        timestamp = matcher.search(scriptblock.group())
        matcher = re.compile('"signature":"([a-z0-9]+)"', re.IGNORECASE)
        signature = matcher.search(scriptblock.group())
        # print [timestamp.group(1), signature.group(1)]

        url = ('http://player.vimeo.com/play_redirect?clip_id=%s&sig=%s'
                '&time=%s&quality=sd' % (id, signature.group(1)
                , timestamp.group(1)))

        r2 = requests.get(url, allow_redirects=False, headers=headers)
        return r2.headers['location']

if __name__ == "__main__":
    # python serve/scraper.py '38681202'
    # http://av.vimeo.com/5207.. 
    if len(sys.argv) > 1:
        print Scraper.get_vimeo(sys.argv[1])
