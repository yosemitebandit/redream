built by Takashi, Bret, Jenn, Mary, Jessica, Kortney, Brianna and Matt
for the Tribeca Hack event in March 2013.


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
* I had a dream where I was watching myself in the mirror and I started to age right in front of my face. My hair turned white and my face wrinkled. It wasn't scary but it was strange (keywords: myself mirror watching age front face hair white face wrinkled scary strange)
