# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 21:20:27 2011

Author: Boris Taratutin, Jaime McCandless
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import HttpLib
from datetime import datetime
from BeautifulSoup import BeautifulSoup


from threading import Thread
from Database.ObjectMappings import Post, ReblogRelations
from NotesScraper import NotesScraper



class PostScraper(Thread):

    type_dict     = {"regular":0, "photo":1, "quote":2, "link":3, "conversation":4, "audio":5, "video":6, "answer":7}
    source_dict   = {"original":0, "reblogged":1, "stolen":2} 

    def __init__(self, url):
        Thread.__init__(self)   # Have to run inherited class' method
        #self.post = Post(url)
        # Post should already be in database - extract it!
        engine = create_engine('sqlite:///Database/Database.db', echo=False) # Link to file
        Session = sessionmaker(bind=engine)
        self.s = Session()
        
        
        self.reblog_map = {} # also returns a reblog map        
        self.urls_found = []
        
        self.post = self.s.query(Post).filter_by(url=url).first()
        if not self.post:
            print "could not find post ", url, " in Database"
            return
        if not self.post.parent_blog:
            print "could not find parent blog for post ", url
            return
        self.url = url
        
        self.s.close()
        
        #self.post.id automatically figured out by object when you initialize it
    
    def extractBasicInfo(self, source):
        """
        Extract basic info from the tags in the source code of the post via
        the tumblr api: type, reblog-key, and date-posted.
        
        Other info available: id, url, url-with-slug, format, state, post content
        """
        soup = BeautifulSoup(source)
        
        try:
            print "Reading post...\n"
            post = soup.tumblr.posts.post
            
        except:
            print "Failed to read post with url:", self.post.url 
            print "WTF mate?"
            print source
            print soup.prettify()

        self.post.type = PostScraper.type_dict[post["type"]]
        self.post.reblog_key = post["reblog-key"]
        self.post.date_posted = datetime.fromtimestamp(int(post["unix-timestamp"]))

        
    def run(self):
        """    
        Organizes the parsing of a tumblr post. For Tumblr posts, you can use
        their api to get some basic info from html tags, but we probably will 
        also need to look at the actual source code to get the rest of the info
        """
        # We can parse tumblr blogs by adding "/<id>" to a regular tumblr query
        # or by changing the "id" value in the api interface. 
        # i.e. http://<blog_name>.tumblr.com/<id> or http://<blog_name>.tumblr.com/api/read?id=<id>
        
        # Here, we use the api interface in the form of 
        # "http://<blog_name>.tumblr.com/api/read/?id=<id>"
        
        # Build query string for the tumblr api
        post_query = "%s%s%s" % (self.post.url[:self.post.url.rfind("/")-5], r"/api/read/?id=", self.post.id)

        # Extract basic post features
        try:
            print "Querying %s" % post_query
            source = HttpLib.openAndRead(post_query)
        except: 
            print "Query failed"
            return
        
        # Extracts easy features, then sends off to notescraper for more work        
        # Fills out post obj. & returns new links for spider
        self.extractBasicInfo(source)
        
        # Check whether this reblog key has already been processed.
        # If it has, no need to process its notes/relations again - they're the same for
        # All reblog relations!
        reblog_key_in_db = self.s.query(ReblogRelations).\
                            filter_by(reblog_key=self.post.reblog_key).first()
        if reblog_key_in_db == None:
            ns = NotesScraper(self.post)
        else:
            print "Reblog key already in DB! No need to process notes"
        
        self.urls_found = ns.all_outgoing_urls
        self.reblog_map = ns.reblog_map
        # passed in post object automatically updated too
        
        self.post.processed = True # Now, we have a fully-filled out post object
        
        try:
            print "postscraper finished processing %s" % self.post.url
            print "reblog map: " % self.reblog_map
            if len(self.reblog_map) > 0:
                print "woo!"
            print self.post
            
        except:
            print "couldn't print %s\n" % self.post.url
            
       
    
if __name__ == "__main__":
    #p = PostScraper(r"http://yourhead.tumblr.com/post/6076335838")
    #p = PostScraper(r"http://naivemelody.tumblr.com/post/6727661044/thereal1990s-fight-club-1999")
    #p = PostScraper(r"http://naivemelody.tumblr.com/post/6727661044")
    p = PostScraper("http://thejuanreyes.tumblr.com/post/1253350929")
    p.run()
    print "\nDone"
