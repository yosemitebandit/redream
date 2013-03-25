built by Takashi, Bret, Jenn, Mary, Jessica, Kortney, Brianna and Matt
for the Tribeca+GAFFTA Hack event in March 2013.

Try the live system at [redream.us](http://redream.us) or
checkout our [demo video](https://vimeo.com/62589601)


### Technical workings - frontend

1. a dream description is submitted
9. you're then taken to a unique url which will eventually host the dream montage
10. while you're waiting, you can see a progress indicator that's based on keyword
classification and the state of the vimeo-scraping
11. you can also give us a twitter handle and we'll message you when the video
is ready
12. once all of the clips have been processed, the progress bar hits 100% and
we automatically reload the page
13. we use popcorn to overlay and cut between each of the hosted mp4s
14. the audio tracks are all played simultaneously


### Technical workings - backend

2. NLTK parses the dream description for keywords, essentially looking for nouns,
verbs and adjectives greater than four characters in length
3. consecutive keywords are grouped together
4. we use the vimeo API to find one video for each of these keyword groups
5. the vimeo search is biased towards choosing a video from the "oldest" category,
but it can also select popular videos.  we also try to favor the shorter videos.
6. our scraper downloads each mp4
7. we crop the video to 5-15% of its full duration, starting somewhere
between 20 and 70% of the total length.  the randomness here should help prevent
a keyword from mapping to the exact same sample every time
8. the cropped video is rehosted on s3
9. ..and so that process is carried out for each keyword group by a worker pool


### Algorithm thoughts

1. take input words
2. find keywords (remove prepositions, articles, etc)
3. search within archives for each major keyword -- an action, object, place (individually); this returns one clip per keyword
4. [optional] limit the results to movies less than 3 minutes
5. take random slice of video [optional] need to keep the rhythm of clips -- duration of slice is determined by number of non-keywords in between the keywords, or user-specified weights; keep a muscial time during the cuts
6. [optional] maybe take steps to elongate certain videos to make up for terse dreams
7. [optional] add audio overlay based on other keywords (freemusicarchive.org or archive.org)
8. glue all videos together (randomly or in sequence)
9. return that compressed video back to the website (probably 640 x 480)


### Example dreams

* went to a party people were throwing hats like frisbees, people were 
flying up the houseboat stairs (keywords: frisbees, stairs, spirals)
* I had a dream where I was watching myself in the mirror and I started to age 
right in front of my face. My hair turned white and my face wrinkled. It 
wasn't scary but it was strange (keywords: myself mirror watching age front 
face hair white face wrinkled scary strange)
* I jumped over the fence of my childhood neighbor’s backyard and there were 
bright pink, blue and orange snakes. It was very frightening and I quickly 
climbed out. 


### Running a worker

we're using [rq](http://python-rq.org).

    $ cd serve
    $ rqworker


### Testing

test the keyword classifier via nose:

    $ nosetests serve


### Running on the server

it's terrible, but we're just running a bare flask server and the workers
behind screen.
here are some helpful commands:

    $ screen -ls  # view sessions
    $ screen -r  # reattach to a session with tab
    $ [Ctrl-a] [c]   # within screen, create a new window
    $ [Ctrl-a] [n], [Ctrl-a] [p]  # within screen, navigate windows
    $ [Ctrl-a] [[]  # within screen, enable scrolling
    $ [Ctrl-d]  # detach screen session
