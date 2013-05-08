#!/usr/bin/python26
"""
Centipede (spider) for analyzing the (Tumblr) blogosphere
sends out scrapers and keeps track of them.

Author: Boris Taratutin, Jason Curtis, Jaime McCandless

Ja3BoPlus@gmail.com
Copyright 2011
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Database.ObjectMappings import *


from threading import Thread
import time
from BlogScraper import BlogScraper 
from PostScraper import PostScraper
from Other.Log import Log
import HttpLib


# Define constants here
MAX_BLOG_SCRAPERS = 3 #10
MAX_POST_SCRAPERS = 15 #20
SAVE_INCREMENT = 50
RUNNING_SAVE_TIME = 45 # seconds to run code before save
NEW_URLS_THRESHOLD = 1000

engine = create_engine('sqlite:///Database/Database.db', echo=False) # Link to file
Session = sessionmaker(bind=engine) # Session is connected to DB

class Centipede:#note CamelCase class name
    """Sends out scraper threads to harvest information from URLs
    
    Keeps track of urls visited to make sure that blogs are not revisited.
    Tries to keep a certain number of scrapers out at all times.
    
    Attributes:
        urls_unvisited: 
            list of urls (strings) to be visited that have not yet been sent out
            for scraping
        
        urls_visited:
            list of urls that have had scrapers sent out for them
        
        max_scrapers:
            maximum number of scrapers out that Centipede attempts to maintain
        
        DB:
            dict where each key is a url and value is the object returned from the
            scraper sent to that url.
            eg. {"www.google.com": <Blog object> }
            Centipede does not control the contents of the objects within it.
        
    """
    

	# Init Method takes a list of unvisited URLs (URLs to crawl) and adds them to our database
	# Of uncrawled URLs. 
    def __init__(self, unvisited_urls):
        self.debugMode = True
        
        self.threads_out = []      
        self.urls_failed = []
        self.threads_finished = 0 # counter for how many threads have finished.
        s = Session() # Connection to DB

        for url in unvisited_urls:
            # If not already in database, add it to search list!
            if not s.query(UnvisitedURLs).filter_by(url=url).first():
                u = UnvisitedURLs(url=url)
                s.add(u)

        s.commit()
        
        # So we can acquire more of these before we have to commit!
        self.unvisited_urls = []
        
        
        
    # The Main thread-generating, process-managing process in centipede
    def run(self):
        
        # Initialize Scrapers
        for i in range(MAX_BLOG_SCRAPERS): #put out initial scrapers
            scraper = self.sendScraper(scr_type="blog") #initializes a new scraper thread.
            if scraper == -1: #no URLS left to scrape
                break
            
        for i in range(MAX_POST_SCRAPERS):
            scraper = self.sendScraper(scr_type="post")
            if scraper == -1:
                break
                
        # Keeps a watch on threads and shoots off their output to be 
        # processed when they finish
        while(True):
            print "\n--checking on %s scrapers" % len(self.threads_out)
            
            
            # Check whether any thread has finished running
            for t in self.threads_out:
                if not t.is_alive():
                    print "%s thread finished!" % t.__class__
                    
                    self.threads_finished += 1 # count our successes!
                    s = Session()
                    
                    # Decide what kind of process finished running, and 
                    # What we should do with it
                    
                    # For Blogs, simply add their info to the list of processed links
                    if t.__class__ == BlogScraper:
                        to_add = t.blog
                        print "BLOG scraper for", t.url, "is done."
                        
                    # For posts, send off their info to be processed into the 
                    # ReblogRelations Table
                    else:
                        to_add = t.post
                        print "POST scraper for", t.url, "is done."
                        res = self.processReblogRelations(t.post, t.reblog_map) # process reblog relations

					# Send the blog/post to be merged with our database
                    self.updateDB(to_add)
                    print "Committed %s!" % to_add.url

                    # Only process new urls if they exceed some amount/threshold
                    # (so can lower # of writes to database)
                    self.unvisited_urls.extend(t.urls_found)                    
                    if len(self.unvisited_urls) > NEW_URLS_THRESHOLD:
                        try:
                            self.assimilateNewUrls(self.unvisited_urls)
                        except AttributeError:
                            err_str = "attributeError:", t,\
                                "failed to complete correctly (url:",t.url,")"
                            print err_str
                            self.urls_failed += t.url
                        
                    # Remove Finished Thread
                    print "REMOVING thread! %s" % t
                    self.threads_out.remove(t)
                    
                # If No threads finished running this cycle, continue..
                else:
                    print "scraper for", t.url, "is still running..."
            
            
            # Try to send out scrapers (blog or post) up to the max limit for each
            # If can't send out any scrapers, means we're done!
            while len(self.threads_out) < MAX_BLOG_SCRAPERS:
                # make an effort to keep the number of scrapers at the limit
                if self.sendScraper(scr_type="blog") == -1:
                    break # there were no urls ready to visit; give up for now
                    
            while len(self.threads_out) < MAX_POST_SCRAPERS:
                # make an effort to keep the number of scrapers at the limit
                if self.sendScraper(scr_type="post") == -1:
                    break # there were no urls ready to visit; give up for now
                
            # End case. heh.
            s = Session()
            if not self.threads_out and not (s.query(UnvisitedURLs).first()):
                print "We're done!\nNo threads out and no unvisited URLs! :)"
                return
            
            # Throttling
            time.sleep(1)    
        
                
    def isPostUrl(self,url):
        """returns true for a url with '/post/' in it"""
        return url.find('/post/') != -1
        
    def getUrlType(self, url):
        """ Returns 0 for 'Blog' and 1 for 'Post' """
        if self.isPostUrl(url):
            return 1
        return 0
    
    def assimilateNewUrls(self, urls):
        """adds urls to the UnvisitedURLs table if we don't have information on them
           in any of our tables"""
           
        # First, 'clean' the new urls - remove duplicates, and trailing slashes, etc.
        urls = HttpLib.cleanLinks(urls)
           
        print "\nAssimilating %s new urls\n" % len(urls)
        if len(urls) <= 0:
            return
            
        s = Session()
        
        
        # For each URL, 
        for url in urls:
            
            # Query the Database & find out if URL already in it
            tables_to_query = [Blog, Post, UnvisitedURLs]
            to_save = True
            for table in tables_to_query:
				# Only care about entries that are fully processed - if they're not, we'll need to scrape them!
				entries = s.query(table).filter_by(url=url,processed=True).first()
			
                # If we found entries (!= None), don't add it to our 'unvisited urls' table
                if entries != None:
                    to_save = False
                    break
                
            if not to_save:
                continue
            
            # If didn't break by this point, then we should add the url to the
            # 'To save' session forthe UnvisitedURLs table
            #print "adding %s to be saved to the unvisited urls table" % url
            u = UnvisitedURLs(url=url)
            u.url_type = self.getUrlType(url)
            s.add(u)
        
            
        print "committing all unsaved urls to the database"
        s.commit()
        print "%s urls now in unvisitedURLs DB\n" % s.query(func.count(UnvisitedURLs))
        urls = []
        self.unvisited_urls = []         
         
    
    def sendScraper(self, scr_type=None):
        """Chooses a url from self.urls_unvisited and sends out an appropriate
        scraper. Returns -1 if there are no unvisited urls left."""
        print "\nRequesting to send out a %s scraper" % scr_type
        s = Session() # Connection to DB
        q = s.query(UnvisitedURLs).first() # Check if there are any urls to scrape
        
        if q == None:
            print "No URLs to scrape"
            print "%s threads still running" % len(self.threads_out)
            return -1
            
        else:
            if scr_type == "blog":
                url_obj_to_scrape = s.query(UnvisitedURLs).filter_by(url_type=0).first()

            elif scr_type == "post":
                url_obj_to_scrape = s.query(UnvisitedURLs).filter_by(url_type=1).first()
            
            # 'getFirstBlog' (or post) return None if can't complete task.
            # In that case,url == None is true, and we can just pop the first one
            if not url_obj_to_scrape:
                print "Couldn't find a %s to process - sending out other type instead" % scr_type
                url_obj_to_scrape = s.query(UnvisitedURLs).first()
                
            print "sending out scraper to ", url_obj_to_scrape
                
            # Decide which scraper to send out
            if self.isPostUrl(url_obj_to_scrape.url):
                scraper = PostScraper(url_obj_to_scrape.url)
            else:                
                scraper = BlogScraper(url_obj_to_scrape.url)
                
            # Remove from to_send_out list
            s.delete(url_obj_to_scrape)
            s.commit()
                
            print "sending out scraper for", url_obj_to_scrape.url
            scraper.start()
            self.threads_out.append(scraper)
            return scraper
            
            
	def processReblogRelations(self, post, reblog_map):
        """ For each post object returned, try to update the ReblogRelations 
            table with all of the information included """

        print "\nProcessing %s Reblog Relations for %s" % (len(reblog_map.keys()), post.url)
        print reblog_map
        
        if len(reblog_map.keys()) <= 0:
            print "nothing to process. returning"            
            return

        # If the post reblog_key is already in this table (anywhere),
        # We can assume that we've already completely processed it 
        # (Because of the way Tumblr works)
        # And can return without doing anything
        s = Session()
        any_entries_in_db = s.query(ReblogRelations).filter_by(reblog_key=post.reblog_key).count()
        if any_entries_in_db > 0:
            print "Reblog relations for %s already processed!" % post.url
            print "Doing nothing."
            return

        # Otherwise, 
        # Iterate through reblog map
        # {'poster':['reblogger1', 'reblogger2',...]}        
        for poster, reblogger_list in reblog_map.iteritems():
            for reblogger in reblogger_list:
                new_relation = ReblogRelations(post.reblog_key, poster, reblogger)
                s.add(new_relation)
                
        s.commit()
        
        
        
        
    def updateDB(self, to_add):
        """ Updates the database (in the correct table) with the given object """
        try:
            print "\nupdating DB to include ", to_add.url
            table_type = self.getUrlType(to_add.url)
            s = Session()
            
            if table_type == 0: #blog
                old_entry = s.query(Blog).filter_by(url=to_add.url).first()
                if old_entry:
                    print "ahhh! we processed a blog we shouldn'tve"
                    print old_entry
                    raise
            else: # post
                print "getting post from db"
                old_entry = s.query(Post).filter_by(url=to_add.url).first()
                print "got post from db"
                
            # if the entry exists at all
            if old_entry:
                old_entry.update(to_add)
                s.commit()
            
                print "successfully updated old entry"
            else:
                print "%s not in database yet. Nothing to remove" % to_add.url
                print "trying to add ", to_add.url, " to Database"
                s.add(to_add)
                s.commit()
                print "successfully added %s to Database" % (to_add.url)
        except:
            print "couldn't add %s to Database" % to_add.url
            #l.write("couldn't add to Database: %s\n" % to_add)            


def main():
    #cent = Centipede(["http://yourhead.tumblr.com/"])
    #cent = Centipede(["http://andthenwefellapart.tumblr.com/"]) #too many posts
    #cent = Centipede(["http://thejuanreyes.tumblr.com", "http://thejuanreyes.tumblr.com/post/7754477210"])
    #cent = Centipede(["http://notveryraven.tumblr.com/"]) #4000 posts
    cent = Centipede(["http://chanaaaa.tumblr.com", "http://notveryraven.tumblr.com/", "http://yourhead.tumblr.com/"]) #1000 posts
    cent.run()

if __name__ == '__main__': 
    #test cases or demos should be put in one of these
    #this will only run if the file itself is run, not imported
    main()
