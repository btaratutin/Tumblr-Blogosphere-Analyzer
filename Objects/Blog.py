# -*- coding: utf-8 -*-
"""


June 21, 2011
"""

import datetime

class Blog:
    
    def __init__(self, url=""):
        """ Initialize the blog object  """
        
        self.url    = url       # The index url of the blog
        self.name   = ""      # The 'name' of the blog (http://(name).tumblr.com)        
        self.title  = ""     # The title of the blog as named by the blogger 
        self.posts  = []     # List of posts within the blog (urls)
        self.last_crawled_date = datetime.date.today()
        
        ### Maybe implement later ###
        # followers = []
        
        
    def getStats(self):
        """ Calculates the 'stats' for the posts of the blog; counts the total
            number of reposts, original posts, and stolen posts.
            
            Returns:
                stats: dictionary {'reposts':0, 'original':0, 'stolen':0}s
        """
        
        pass
    
    
    def __str__(self):
        return """
url: %s\t\t
name: %s\t\t
title: %s\t\t
posts: %s\t\t
crawl date: %s\t\t
        """ % (self.url, self.name, self.title, self.posts, self.last_crawled_date)
        

