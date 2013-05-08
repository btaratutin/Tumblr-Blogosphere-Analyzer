# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 21:51:40 2011

@author: btaratutin
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from ObjectMappings import *


import sys
import os
sys.path.append(os.path.split(os.getcwd())[0])

import PostScraper



def cleanUnvisitedURLs(s):
    """ removes any links from unvisitiedURLS that would cause an overwrite problem """
    blog_urls_processed = s.query(Blog).filter_by(processed=True).values("url") # returns iterator
    #blog_urls_processed = [b[0] for b in blog_urls_processed] # convert to list
    
    print "processed blog urls: %s" %     blog_urls_processed
    
    for url in blog_urls_processed:
        url=url[0] #stupid tuple notation
        print "url: %s" % url
        #blog = s.query(UnvisitedURLs).filter_by(url=url)
        blog = s.query(UnvisitedURLs).get(url)
        if blog: # if it's processed and in the 'unvisited urls', then remove it!
            print "%s is processed and in UnvisitedURLS. Removing it from DB" % url
            print blog            
            s.delete(blog)
            
    
    print "committing deletes to db"
    s.commit()
    print "done!"
    
    
    
    
print "Attempting to load objects from database\n"
engine = create_engine('sqlite:///Database.db', echo=False) # Link to file
Session = sessionmaker(bind=engine)
s = Session()

print "Retrieving all Blog Contents"
res = s.query(Blog).all()

print "\nRetrieving all Post Contents"
res2 = s.query(Post).all()

print "\n\n"
print "num. blogs: %s" % len(res)
print "num. posts: %s" % len(res2)
print "\n\n"

url = "http://chanaaaa.tumblr.com/post/6612843764"

posts = s.query(Post).filter_by(id=5595274547).all()

print posts

blogs = s.query(Blog).filter_by(url="http://felicialovesyu.tumblr.com/").all()
print blogs

#print "\n%s processed posts" % len(posts)



#print "matching post entry: %s" % post_entry

"""
tables_to_query = [Blog, Post, UnvisitedURLs]
for table in tables_to_query:
    entries = s.query(table).filter_by(url=url).first()
    print "num entries:"
    print entries
    
    
    # If we found entries, don't add it to our 'unvisited urls' table
    if entries != None:
        print "%s already in table %s" % (url, table)
        break
    
print "acquiring and deleting first query in blogs"
first_entry = s.query(Blog).first()
s.delete(first_entry)
s.commit()
"""

print "\n\n\n"

cleanUnvisitedURLs(s)




    
#print posts