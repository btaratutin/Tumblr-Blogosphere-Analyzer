# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 20:16:01 2011

"""

from datetime import datetime

import sys
import os
sys.path.append(os.path.join(os.getcwd(), "Other"))
import DictTools

class Post:
    type_dict     = {0:"regular", 1:"photo", 2:"quote", 3:"link", 4:"conversation", 5:"audio", 6:"video", 7:"answer"}
    CSV_header    = "Url, ID, Type, Reblog-Key, Date Posted, Num. Notes, Num. Reblogs, Num. Likes"
    
    def __init__(self, url=""):
        
        # These are populated by PostScraper
        self.url            = url
        self.id             = 0
        self.parent_blog    = None          # For now, don't reference - Pickle might not like

        self.date_posted    = ""
        self.type           = 0             # 0: regular, 1: photo, 2: quote, 3: link, 4: conversation, 5: audio, 6: video, 7: answer
        self.reblog_key     = ""
        self.last_crawled_date = datetime.now()

        # These still need to be done        
        self.source         = 0             # 0: original, 1: reblogged, 2: stolen
        self.source_url     = ""            # This post's url if original, otherwise the url of the post it was reblogged/stolen from


        self.num_notes      = 0
        self.num_comments   = 0
        self.num_likes      = 0
        self.num_reblogs    = 0
        self.reblog_map     = {}            # {'poster':['reblogger1', 'reblogger2',...]}
                                            # A mapping that explains who has reblogged who for this post
        
    def toString(self):
        print "url: \t\t" + self.url
        print "id: \t\t" + str(self.id)
        print "type: \t\t" + Post.type_dict[self.type]
        print "reblog-key: \t" + self.reblog_key
        print "post date: \t\t" + str(self.date_posted)
        print "crawl date: \t" + str(self.last_crawled_date)
        
        print "\n"        
        
        print "num. notes: \t%s" % self.num_notes
        print "num. reblogs: \t%s" % self.num_reblogs
        print "num. likes: \t%s" % self.num_likes
        print "num. comments: \t%s" % self.num_comments
        
        print "\n"
        
        N=6
        print "Top %s posters:" % N
        for p in self.topPosters(N):
            print "  %s: %s" % p
            
            
    def toCSVStr(self):
        return "%s,%s,%s,%s,%s,%s,%s,%s" \
            % (self.url, self.id, self.type_dict[self.type], self.reblog_key, self.date_posted,
               self.num_notes, self.num_reblogs, self.num_likes)
        
        
    def topPosters(self, N=10):
        """ returns the top N 'posters' (ppl reblogged the most) for this post """
        reblog_hist = DictTools.convertToHistogram(self.reblog_map)
        return DictTools.sortDict(reblog_hist, key=1, reverse=True)[:N]
        
