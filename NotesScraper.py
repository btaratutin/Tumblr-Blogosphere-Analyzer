# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 22:44:23 2011

Author: Boris Taratutin

"""

import HttpLib
import re
from BeautifulSoup import BeautifulSoup


# Our Methods
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "Other"))
import DictTools


class NotesScraper():
    
    def __init__(self, post):
        self.post = post
        self.reblog_map = {}
        self.all_outgoing_urls = []
        
        self.run()
    
    def getNextPageOfNotes(self, content, url):
        """ Parses the page, finds the link to "view more notes" (or equivalent),
            and returns a full url that points to the next page of notes """
        print "processing next page of notes.. (%s)" % url
        
        # Find tumblr's link to the next 'notes' page (hidden away in javascript crap)
        note_url = re.search(r"tumblrreq.open\('get','(?P<note_url>.*?)',true\);", content, re.I)
    
        try:
            # Extract the url to the note
            note_url = note_url.group('note_url')
        except:
            print "No more pages of notes to process"
            return -1
        
        # get "http://(name).tumblr.com" - so we can add the extracted notes url to it
        # (no trailing slash "/" included)
        base_url = HttpLib.extractBaseUrl(url)     
        next_query = base_url + note_url    # "note url" is case sEnSiTiVe!!
        
        #print "note url: %s\nnext query: %s\n" % (note_url, next_query)
        return next_query
        
          
    
    def parseNotes(self, url, num_likes=0, num_comments=0):
        # AAHHH DONT PASS IN dictionary here!! values transfer over :( (it's not mutable))
        """ Parses all of the notes (reblogs, likes, and comments) for the given
            post URL.
            
            Returns tuple: (num_likes, num_comments, reblog_map) """
            
        print "reblog dict at start of parsenotes:" % self.reblog_map
            
        content = HttpLib.openAndRead(url, lower=False)
        soup = BeautifulSoup(content)
        
        # Otherwise, parse the links and likes, etc. off the page
        
        try:
            notes = soup.ol.findAll('li')
        except:
            print "no notes on page %s" % url
            return (0, 0)
        
        print "processing %s notes from %s" % (len(notes), url)
        
        for note in notes:
            try:
                words = note["class"].split()   # extract the contents of the 'class' tag
            except:
                continue
            note_type = words[1]
            print "\nNote type: %s" % note_type
            
            # The convention will be "<person 1> reblogged <person 2>"
            # We find those two links and extract their URLs
            # (Where the 'x reblogged y' info comes from)
            
            if note_type == "reblog":
                try:
                    details = note.span.findAll('a')         
                    print "details: %s\n" % details                
    
                    poster = details[1]['href']
                    print "poster: %s" % poster
    
                    reblogger = details[0]['href']
                    print "reblogger: %s" % reblogger
                    
                    
                    # Add to results (reblog_map)
                    print "adding to map"
                    self.reblog_map[poster] = self.reblog_map.get(poster, [])
                    if reblogger not in self.reblog_map[poster]:
                        self.reblog_map[poster].append(reblogger)
                    
                except:
                    print "Couldn't extract reblog relation(%s). Skipping for now" % details
                    # Probably a 'posted by' superflous error - as 
                    details = note.span.findAll('a')
                
            elif note_type == "like":
                num_likes += 1
                
            elif note_type == "more_notes_link_container":
                num_comments += 1
               
    
        # Figure out what to do next
        next_query = self.getNextPageOfNotes(content, url)
    
        print "\nreturning %s, %s, %s notes processed for %s" \
            % (num_likes, num_comments, self.reblog_map, url)
        
        if next_query == -1:
            print "nothing else to query"
            return (num_likes, num_comments)
        else:
            print "more pages to query - getting more"
            (num_likes, num_comments) = self.parseNotes(next_query, num_likes, num_comments)
            return (num_likes, num_comments)
            
    
        
    def run(self):
        """ Fills out the information in the post object and returns a list
            of URLs for the spider to process """
        (num_likes, num_comments) = self.parseNotes(self.post.url)
        
        self.post.num_likes = num_likes
        self.post.num_comments = num_comments
        self.post.num_reblogs = sum(DictTools.convertToHistogram(self.reblog_map).values())
        
        self.post.num_notes = self.post.num_likes + self.post.num_comments + self.post.num_reblogs
        
        for link_lists in self.reblog_map.values():
            self.all_outgoing_urls.extend(link_lists)
            
        print "found %s outgoing links\n" % len(self.all_outgoing_urls)

        


if __name__ == "__main__":
    pass
    ### TESTING JUST THE CODE ###    
    from Database.ObjectMappings import Post
    a = NotesScraper(Post("http://yourhead.tumblr.com/post/355481999/this-is-my-new-favorite-tumblr"))    
    print a
    #x = parseNotes("http://yourhead.tumblr.com/post/5771380712/maybe-the-best-conversation-i-have-ever-had")
    #x = parseNotes("http://chanaaaa.tumblr.com/post/5326278147")
    #x = parseNotes("http://yourhead.tumblr.com/post/355481999/this-is-my-new-favorite-tumblr")
    #print x
    
    #p = Post("http://thejuanreyes.tumblr.com/post/1253350929")
    #p = Post("http://yourhead.tumblr.com/post/5288297214")
    #outgoing_urls = run(p)
    #print p.toString()
    #print "outgoing urls",outgoing_urls
    
    
    ### TESTING WITH POST OBJECT ###
    
    """    
    import sys
    sys.path.append(os.path.join(os.getcwd(), "Objects"))
    from Post import Post
    
    p = Post(r"http://suisjeegoist.tumblr.com/post/6951762478")
    urls = run(p)
    print urls
    print p.toString()
    """
    
    # THE HIPSTER DOWSING ROD!!
    
    # Runtime note: 2,432 notes take 1:37 (MM:SS) to process (.041s/note)
    
