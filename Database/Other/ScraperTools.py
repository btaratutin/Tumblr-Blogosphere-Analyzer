# -*- coding: utf-8 -*-
"""
Created on Mon Jul 04 16:32:38 2011

@author: btaratutin

Generic tools to help in scraper-like applications; extracting url content, etc.
Specific to Tumblr
"""

def isBlog(url):
    """ Determines whether the url is a 'main blog' page or not.
        If it is, then '.tumblr.com(/)' should be the last thing in the url """
    return url.find('.tumblr.com') + 12 >= len(url)
    
def isPost(url):
    """ Determines if url is a post by searching for 'post' in url """
    return url.find('/post/') != -1
    

def getFirstBlog(url_list):
    """ Returns the first 'blog' type of url in the list.
        Assumes url_list is not empty.
        If can't find, returns -1"""
    for i, url in enumerate(url_list):
        if isBlog(url):
            return url_list.pop(i)
    return None
    
def getFirstPost(url_list):
    """ Returns the first 'post' type of url in the list.
        Assumes url_list is not empty.
        If can't find, returns -1"""
    for i, url in enumerate(url_list):
        if isPost(url):
            return url_list.pop(i)
    return None
    
def extractBlogName(self, blog_url):
        """ Extracts the blog name from a url (removes html url superfluity) """
        blog_core = re.search(r"((http://)|(www.))(?P<core>(.*?)).tumblr.com", blog_url)
        return blog_core.group('core')