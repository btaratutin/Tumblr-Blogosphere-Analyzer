# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 21:51:29 2011

@author: btaratutin
"""

# Tries to add information to our database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from ObjectMappings import *


print "Attempting to create objects & save them to the database"


engine = create_engine('sqlite:///Database2.db', echo=False) # Link to file
Session = sessionmaker(bind=engine)


# Add Blog Objects
b = Blog(url="http://naievemelody.com")
b.name="Melody"
b.title="PooPoo"

# Add Post Objects
p = Post(url="helooooo27", parent_blog="ahahahahaha22.comssss")
p.id=505

p2 = Post(url="post2")

# Save Everything
s = Session()
s.add(b)
s.add(p)
s.add(p2)

# Commit
s.commit()
print "Success!"


# Unvisited Urls
u = UnvisitedURLs(url="unvisited1ss")
u.url_type = 0

# MOAR Blogs
b2 = Blog("ahahahahaha22.comssss")
b2.posts = ['helooooo27', 'post2']

# Commit
s.add(u)
s.commit()


