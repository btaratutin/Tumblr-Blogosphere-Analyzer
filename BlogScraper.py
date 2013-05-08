# -*- coding: utf-8 -*-
"""

'Scrapes' the content of a (tumblr) blog to populate some basic information
about the blog and return a list of post links (all of that blog's posts).

In order to do this, we must parse each section of the 


TODO: make this able to interface with other (non-tumblr) blogs?


Authors:    Boris Taratutin
            Jaime McCandless

Last Modified: June 20, 2011
Copyright 2011
                
"""

import re
import HttpLib
from BeautifulSoup import BeautifulSoup

from threading import Thread
from Database.ObjectMappings import Blog
from Database.ObjectMappings import Post




class BlogScraper(Thread):
    
    ### Methods that might be useful outside of this
    
    def __init__(self, url):
        Thread.__init__(self)
        self.blog = Blog(url)
        self.url = url
        self.urls_found = []

        try:
            self.blog.name = self.extractBlogName(self.blog.url)
        except:
            print '\n\n\ncould not extract blog name from %s' % self.blog.url
            self.blog.name = ""
            raw_input()
        
    def extractBlogName(self, blog_url):
        """ Extracts the blog name from a url (removes html url superfluity) """
        blog_core = re.search(r"((http://)|(www.))(?P<core>(.*?)).tumblr.com", blog_url)
        return blog_core.group('core')
    
    
    ### Methods specific to our application
    
    def getBlogPosts(self, content, blogname):
        """ Returns 'Post' objects with only their 'url' attribute filled out
            Gets all of the posts on a page, but only the ones that link to the
            'mother blog' - not to others. Essentially a page's internal links 
            
            Args:
                blog: the title of the blog (no url), ie. 'naivemelody' """
        soup = BeautifulSoup(content)
        post_urls = soup.findAll('post')
        
        posts = [] # a list of 'Post' objects that we'll insert into the DB
        
        for post in post_urls:
            # Only save posts that belong to the 'mother blog'
            url = post["url"]
            url = HttpLib.cleanLinks([url])[0]
            if self.extractBlogName(url) == blogname:
                #posts.append(Post(url=url))
                posts.append(url)
    
        #print "found posts for %s!" % blogname
        #print posts
        return posts
        
    def extractBasicTumblrInfo(self, content, soup, blog_title):
        """ Extracts basic info about the blog - ie. how many posts it has! """
        
        try:
            #TODO: convert to beautiful soup?
            #TODO: speed test between regex and beautifulsoup
            
            num_posts = int(soup.tumblr.posts["total"])
            
            #num_posts = re.search(r"<posts.*?total=\"(?P<num_posts>\d*?)\"", content)
            #num_posts = int(num_posts.group('num_posts'))
        except:
            num_posts = 0
            print "Can't calculate num posts!"
            raise
            # TODO: add code that deals with this if it happens!
        
        return {'num_posts': num_posts}
        
    
    def redundancyCheck(self, all_blog_posts, new_posts):
        """ Does a sanity check - checks if new posts are all already within the 
            'all blog posts', then something's wrong & we should quit.
            
            Returns 'True': there <is> a new post - everything working ok
            Returns 'False': all posts are old, some error occured"""
        for post in new_posts:
            if post not in all_blog_posts:
                return True
        
        return False
    
    def run(self):
        """ Generates the populated blog object 
        
        Organizes the parsing of a tumblr blog. For Tumblr blogs, you can use
        their api to get 50 posts at a time - scraping until we get no more posts
        """
        
        # We can parse tumblr blogs by adding "/page/n" to a regular tumblr query
        # or by changing the "start=n" value in the api interface._
        
        # Here, we use the api interface in the form of 
        # "http://(blogname).tumblr.com/api/read/?num=50start=n"
        # We put in the blog's name, and go through the posts by 50 until we run out
        offset = 0      # the post # we start querying the next 50 from
        
        # Extract blog title and build query string for the tumblr api
        blog_query = r"http://" + self.blog.name + r".tumblr.com/api/read/?num=50&start=" + str(offset)
        
        # Extract basic blog feature
        content = HttpLib.openAndRead(blog_query)
        soup = BeautifulSoup(content)
        basic_info = self.extractBasicTumblrInfo(content, soup, self.blog.name)
        
        num_posts = basic_info['num_posts']
        print "processing until %s posts\n" % num_posts
        
        
        # Walk through each set of 50 posts of the blog until get to end post
        while offset <= num_posts:
            try:
                print "querying %s" % blog_query
                source = HttpLib.openAndRead(blog_query)
            except:
                print "sanity check failed"
                raise
        
            new_posts = self.getBlogPosts(source, self.blog.name)    ## The actual feature extraction
            self.urls_found.extend(new_posts) # for scraper
            print "%s new posts urls for %s:" % (len(new_posts), self.blog.name)
            
            print "%s old posts in %s:" % (len(self.blog.posts), self.blog.name)
            
            if self.redundancyCheck(self.blog.posts, new_posts):
                for i, post in enumerate(new_posts):
                    self.blog.posts.append(Post(post))
            else:
                print "redundancy check failed - same content returned as prev. run"
                raise
            
            # Set-up for next run
            blog_query = blog_query.rstrip(str(offset))
            offset += 50
            blog_query += str(offset)
            
            #print "\n%s of the posts: " % len(new_posts)
            #print new_posts
        
        
        #self.urls_found = list(new_posts) # make new list
        # self.blog modified
        
        self.blog.processed=True
        print "finished processing blog %s" % self.blog.url
        #print "Blog Object Print:"
        #print self.blog
        #return self.blog
    
    
if __name__ == "__main__":
    b = BlogScraper(r"http://designdisorder.tumblr.com/")
    b.run()