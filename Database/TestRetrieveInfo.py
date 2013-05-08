# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 21:51:40 2011

@author: btaratutin5
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from ObjectMappings import *

print "Attempting to load objects from database\n"

engine = create_engine('sqlite:///Database.db', echo=False) # Link to file
Session = sessionmaker(bind=engine)

s = Session()

print "Retrieving all Blog Contents"
num_blogs = s.query(Blog).count()

print "\nRetrieving all Post Contents"
num_posts = s.query(Post).count()
processed_posts = s.query(Post).filter_by(processed=True).count()

print "\nRetrieving all Unvisited URLs"
num_unvisited_urls = s.query(UnvisitedURLs).count()
num_unvisited_blogs = s.query(UnvisitedURLs).filter_by(url_type=0).count()
num_unvisited_posts = s.query(UnvisitedURLs).filter_by(url_type=1).count()
#num_unvisited_posts = num_unvisited_urls - num_unvisited_blogs

print "\nRetrieving all Reblog Relations"
num_reblog_relations = s.query(ReblogRelations).count()



print "\n\n"
print "num. blogs: %s" % num_blogs
print "num. posts: %s" % num_posts
print "num. processed posts: %s" % processed_posts
print "num. reblog relations: %s" % num_reblog_relations
print "\n"
print "num. unvisited urls: %s" % num_unvisited_urls
print "num. unvisited blogs: %s" % num_unvisited_blogs
print "num. unvisited posts: %s" % num_unvisited_posts
