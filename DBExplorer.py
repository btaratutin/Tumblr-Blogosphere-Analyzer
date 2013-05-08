# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 21:02:40 2011

@author: Jason
"""

import pickle
import BlogScraper
import PostScraper
import os


import sys
sys.path.append(os.path.join(os.getcwd(), "Other"))
sys.path.append(os.path.join(os.getcwd(), "Objects"))
from Post import Post




db = pickle.load( open( "DB.p" ) )

blogs = db['blogs']
posts = db['posts']
unvisited_urls = db['unvisited_urls']

#print unvisited_urls



print "\nUnvisited urls: %s" % len(unvisited_urls)
print "Num. blogs: %s" % len(blogs)
print "Num. posts: %s" % len(posts)





for blog in blogs:
    
    name = "%s\\db\\Blog - %s.txt" % (os.getcwd(), blog.name)
    f = open(name, 'w')
    f.write(str(blog))
    f.close()
    
    
name ="%s\\db\\_Posts.csv" % (os.getcwd())
f = open(name, 'w')
f.write("%s\n" % Post.CSV_header)

for post in posts:
    f.write("%s\n" % post.toCSVStr())
        
    



"""
for post in posts:
    print post.toString()
"""