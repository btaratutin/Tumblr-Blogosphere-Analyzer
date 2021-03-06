# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 22:40:47 2011

Aurhor : Jaime McCandless, Boris Taratutin
"""

import urllib2

### Gen. Purpose methods that might not be useful outside of this
def openAndRead(url, attempt = 1, lower=True):
    """ takes a url (string) and returns the html source code for that 
        page (string)"""
    try:
        opener = urllib2.build_opener()
    except:
        print "Failed to init build opener"

    #opener.addheaders = [('User-agent', 'Mozilla/5.0')]     # Need these so can access wikipedia

    try:
        file_in = opener.open(url)
        page_source = file_in.read()
    except urllib2.URLError:
        if attempt < 10:
            print "Url open attempt failed, retrying: attempt ", attempt            
            page_source = openAndRead(url, attempt + 1)
        else: 
            raise
        
    # Lowercase everything to make it easier to process
    if lower:    
        return page_source.lower()
    else:
        return page_source

def cleanLinks(links):
    """ 'Cleans' the links - removes any "#(whatever)" designations, and makes 
        sure there aren't any duplicate links """
        
    # Remove any non-tumblr links
    to_remove = []
    for i, link in enumerate(links):
        if link.find('.tumblr.com') == -1:
            to_remove.append(link)
        else:
            # Normalizing factors - adding trailing slash, removing www.

            # Remove trailing "/" if doesn't exist            
            if link[-1] == "/":
                link = link[:-1]
            
            # Remove "www." if exists
            www_index = link.find("www.")
            if www_index != -1:
                link = link[:www_index] + link[www_index+4:]
                
            # Add "http://" to front
            if not link.startswith("http://"):
                link = "http://" + link
 
                
            # Update link
            links[i] = link
            
    for link in to_remove:
        links.remove(link)
    
    """
    # Get rid of '#' marks on links
    for i, link in enumerate(links):
        if link.find('#') != -1:
            links[i] = link[:link.find('#')]
    """            
        
    # Remove any duplicate links and return
    return removeDuplicates(links)
    
def removeDuplicates(l):
    """ removes any duplicate values in a list """
    return list(set(l))
    
def extractBaseUrl(url):
    """ Extracts the 'base' tumblr url: "http://(name).tumblr.com/"
        from any link given (usu. '/post/' or '/note/' etc.)
        
        Returns modified (base) url
    """  
    
    return url[:url.index('.com')+4]
    
    
def addUrls(url1, url2):
    """ Adds the two urls and makes sure that there are no extra '/' characters
        between them
    """
    pass
    #TODO: build this method - more robust
    
    
if __name__ == "__main__":
    
    print cleanLinks(["http://yourhead.tumblr.com/post/904329500"])
    print cleanLinks(["http://www.google.com"])
