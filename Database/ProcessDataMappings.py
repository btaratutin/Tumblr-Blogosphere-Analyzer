# -*- coding: utf-8 -*-
"""
Created on Wed Aug 03 19:33:24 2011

@author: btaratutin
"""

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref


Base = declarative_base()



class PostData(Base):
    __tablename__ = "PostData"
    
    id              = Column(Integer, primary_key=True, autoincrement=True)
    reblog_key      = Column(Integer, ForeignKey("Posts.reblog_key")) #
    poster          = Column(String, ForeignKey("Blogs.url"))
    reblogger       = Column(String, ForeignKey("Blogs.url"))
    # relationship("Post", backref="parent_blog")
    # parent_blog_url = Column(String, ForeignKey('Blogs.url'))
    
    def __init__(self, reblog_key, poster="", reblogger=""):
        self.reblog_key = reblog_key
        self.poster = poster #could be a problem
        self.reblogger = reblogger # could be a problem
        
    def __repr__(self):
        return "\n id:\t\t\t%s\n reblog key:\t\t%s\n poster:\t\t%s\n reblogger:\t\t%s\n" \
            % (self.id, self.reblog_key, self.poster, self.reblogger)
            
            
    
def createDB(dbname="ProcessedData.db"):
    print "Initializing Database\n"
    
    engine = create_engine('sqlite:///%s' % dbname, echo=False) # Link to file
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)    # Generate data tables
    
    print "Success! Initialized %s" % dbname
    


if __name__ == "__main__":
    createDB("ProcessedData.db")