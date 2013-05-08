# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 20:50:26 2011

Boris Taratutin
July 13, 2011

Initializes the blank databases for the BlogScraper Project:
    - BlogDB
    - PostDB
    - (Relational Mapping 1)
    - (Relational Mapping 2)
    
Setting up a DB:
    http://www.sqlalchemy.org/docs/orm/tutorial.html
"""
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

import datetime
from Other import DictTools
from Other import ScraperTools

Base = declarative_base()

class Blog(Base):
    __tablename__ = 'Blogs'
    
    #id      = Column(Integer, primary_key=True, autoincrement=True)
    #sqlite_autoincrement=True
    url     = Column(String, primary_key=True)
    name    = Column(String)
    title   = Column(String)
    
    processed           = Column(Boolean)
    last_crawled_date   = Column(DateTime)
    
    posts = relationship("Post", backref="parent_blog")
    # , backref="parent_blog"
    # If define backref, don't have to specify it in the child table - it will
    # automatically be created
    
    
    def __init__(self, url="", processed=False):
        """ Initialize the blog object  """
        
        self.url    = url       # The index url of the blog
        self.name   = ""        # The 'name' of the blog (http://(name).tumblr.com)        
        self.title  = ""        # The title of the blog as named by the blogger 
        self.last_crawled_date = datetime.datetime.now()
        self.processed=processed
        self.posts = []
        
        ### TODO ###
        # self.posts  = []        # List of posts within the blog (urls)
        # followers = []
    
    def __repr__(self):

        repr_str = ""
        for p in self.posts:        
            repr_str += "\t%s\n" % p.url
        
        return """
processed: \t\t%s
url: \t\t%s
name: \t\t%s
title: \t\t%s
crawl date: \t%s
posts: \n%s
""" % (self.processed, self.url, self.name, self.title, self.last_crawled_date, repr_str)    
    
    
class Post(Base):
    __tablename__ = 'Posts'
    
    url             = Column(String, primary_key=True)
    id              = Column(Integer)
    reblog_key      = Column(Integer)
    post_type       = Column(Integer) # 0: regular, 1: photo, 2: quote, 3: link, 4: conversation, 5: audio, 6: video, 7: answer

    #parent_blog -- specified as a relationship backref
    parent_blog_url = Column(String, ForeignKey('Blogs.url')) # Nice to do (specify a foreignkey) - but not absolutely necessary
    
    processed       = Column(Boolean)   # Has this post object been filled out/processed?
    date_posted         = Column(DateTime)
    last_crawled_date   = Column(DateTime)
        
    source          = Column(Integer)   # 0: original, 1: reblogged, 2: stole
    source_url      = Column(String)    # This post's url if original, otherwise the url of the post it was reblogged/stolen from
    
    num_notes       = Column(Integer)
    num_comments    = Column(Integer)
    num_likes       = Column(Integer)
    num_reblogs     = Column(Integer)
    
    # Personal Class Stuff
    type_dict     = {0:"regular", 1:"photo", 2:"quote", 3:"link", 4:"conversation", 5:"audio", 6:"video", 7:"answer"}
    CSV_header    = "Url, ID, Type, Reblog-Key, Date Posted, Num. Notes, Num. Reblogs, Num. Likes"
    
    def __init__(self, url="", processed=False):
        
        # These are populated by PostScraper
        self.url            = url
        self.id             = url[url.rfind("/")+1:]    # automatically extract from the id
        self.reblog_key     = 0
        self.post_type      = 0             # 0: regular, 1: photo, 2: quote, 3: link, 4: conversation, 5: audio, 6: video, 7: answer

        self.processed      = processed # by default, not filled out
        self.date_posted    = None
        self.last_crawled_date = datetime.datetime.now()
        
        # These still need to be done        
        self.source         = 0             # 0: original, 1: reblogged, 2: stolen
        self.source_url     = ""            # This post's url if original, otherwise the url of the post it was reblogged/stolen from


        self.num_notes      = 0
        self.num_comments   = 0
        self.num_likes      = 0
        self.num_reblogs    = 0
        
        # TODO
        #self.reblog_map     = {}            # {'poster':['reblogger1', 'reblogger2',...]}
                                            # A mapping that explains who has reblogged who for this post
                                            

        # May be instatiated before the parent_blog is        
        # Finds the parent blog in the database associated with it
        """
        if self.parent_blog == None:
            parent_blog_url = ScraperTools.extractBlogName(self.url)            
            
            engine = create_engine('sqlite:///Database/Database.db', echo=False) # Link to file
            Session = sessionmaker(bind=engine)
            s = Session()
            
            parent_blog = s.query(Blog).filter_by(url=parent_blog_url)
            
            self.parent_blog = parent_blog
        """
                         
    def __repr__(self):
        
        """
        # Calc top posters
        N = 6
        top_poster_str = "Top %s posters:\n" % N
        for p in self.topPosters(N):
            top_poster_str += " %s: %s\n" % p
        """
        
        # Return repr
        return """
processed: \t%s
url: \t\t%s
id: \t\t%s
post type: \t\t%s
parent blog: \t%s

reblog-key: \t%s
post date: \t\t%s
crawl date: \t%s       
        
num. notes: \t%s
num. reblogs: \t%s
num. likes: \t%s
num. comments: \t%s

""" % (self.processed, self.url, self.id, Post.type_dict[self.post_type], self.parent_blog.url,
       self.reblog_key, self.date_posted, self.last_crawled_date,
       self.num_notes, self.num_reblogs, self.num_likes, self.num_comments)
            
            
    def update(self, p):
        """ Updates the attributes of this object to match those of post p """
        self.reblog_key     = p.reblog_key
        self.post_type      = p.post_type

        self.processed      = p.processed
        self.date_posted    = p.date_posted
        self.last_crawled_date = p.last_crawled_date
             
        self.source         = p.source 
        self.source_url     = p.source_url


        self.num_notes      = p.num_notes
        self.num_comments   = p.num_comments
        self.num_likes      = p.num_likes
        self.num_reblogs    = p.num_reblogs
        
        #self.reblog_map     = p.reblog_map 
        
    def toCSVStr(self):
        return "%s,%s,%s,%s,%s,%s,%s,%s" \
            % (self.url, self.id, self.type_dict[self.type], self.reblog_key, self.date_posted,
               self.num_notes, self.num_reblogs, self.num_likes)
        
        
    def topPosters(self, N=10):
        """ returns the top N 'posters' (ppl reblogged the most) for this post """
        #reblog_hist = DictTools.convertToHistogram(self.reblog_map)
        #return DictTools.sortDict(reblog_hist, key=1, reverse=True)[:N]
        return []


class UnvisitedURLs(Base):
    __tablename__ = "UnvisitedURLs"
    
    url         = Column(String, primary_key=True)
    url_type    = Column(Integer) # 0='Blog', 1='Post'
    
    def __init__(self, url=""):
        self.url        = url
        self.url_type   = 0
        
    def __repr__(self):
        return "\nurl: \t%s\ntype: \t%s" % (self.url, self.url_type)


class ReblogRelations(Base):
    __tablename__ = "ReblogRelations"
    
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

def createDB(dbname="Database.db"):
    print "Initializing Database\n"
    
    engine = create_engine('sqlite:///%s' % dbname, echo=False) # Link to file
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)    # Generate data tables
    
    print "Success! Initialized %s" % dbname
    


if __name__ == "__main__":
    createDB("Database2.db")