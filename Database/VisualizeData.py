# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 00:56:58 2011

@author: btaratutin
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ObjectMappings import *
import re


def calcAllDegrees(key_relations):
    """ Give it a bunch of key relations, will return something with all the degrees"""

    for elem in key_relations:
        if hasattr(elem, 'degree'):
            continue
        
        elem.degree = calcFullInDegree(key_relations, elem, 0)
        
    return key_relations


def calcFullInDegree(reblog_map, blogger, degree=0):
    """ Calculates the total sum of the in-degrees pointing to the given blogger """
    
    


def saveToCSV(reblog_map, filename="output3.csv"):
    f = open(filename, 'w')
    f.write("Id,Target,Source,Label\n")
    
    for elem in reblog_map:
        try:
            f.write("%s,%s,%s,%s\n" % \
            (elem.id, elem.poster, elem.reblogger, extractBlogName(elem.poster)))
        except:
            continue
    
    """
    for elem in reblog_map:
        f.write("%s,%s,%s,%s\n" % \
            (elem.id, elem.reblog_key, elem.poster, elem.reblogger))
    """
    
    f.close()
    

def getNumReblogs(blogger, reblog_map):
    """Returns the number of rebloggers for a given post
        Reblog map: ("""
    num_reblogs = 0
    for relation in reblog_map:
        if relation.poster==blogger:
            num_reblogs += 1
            
    return num_reblogs

def extractBlogName(blog_url):
    """ Extracts the blog name from a url (removes html url superfluity) """
    blog_core = re.search(r"((http://)|(www.))(?P<core>(.*?)).tumblr.com", blog_url)
    if blog_core:
        return blog_core.group('core')
    else:
        print "can't extract from %s" % blog_url
        return blog_url

def visualizeGraph(s, N=10, minsize=5, maxsize=15):
    """We will plot up to N graphs for each reblog_key."""
    import networkx as nx
    import numpy as np
    import matplotlib.pyplot as plt
    import random
    from operator import itemgetter
    
    # Get first N reblog keys from the ReblogRelations table
    # (These will include all of the posters & rebloggers)
    print "starting to visualize graph"
    
    g = nx.DiGraph()          # Create empty graph; no nodes, no edges
    
    unique_reblog_keys = s.query(distinct(ReblogRelations.reblog_key)).all()
    print "found %s unique reblog keys" % len(unique_reblog_keys)
    # returns list of tuples - with first value being 
    
    
    print "processing reblog key frequencies"
    reblog_key_freq_pairs = []    
    
    for key in unique_reblog_keys:
        occurances = s.query(ReblogRelations).filter_by(reblog_key=key[0]).count()
        new_pair = (key[0], occurances)
        reblog_key_freq_pairs.append(new_pair)
        
    # Now we have a list of (reblog_key, occurance)
    
    # Sort by the occurances, highest values first
    reblog_key_freq_pairs.sort(key=itemgetter(1), reverse=True)
    
    
    #####
    biggest_weight = reblog_key_freq_pairs[0][0]
    key_relations = s.query(ReblogRelations).filter_by(reblog_key=biggest_weight).all()
    saveToCSV(key_relations)
    return
    #####
    
    
    #random.shuffle(reblog_key_freq_pairs)
    print "\nFound sorted reblog key frequency pairs:"
    print reblog_key_freq_pairs

    # Extract the N reblog keys that we will actually process    
    #reblog_key_clusters = [reblog_key for reblog_key,occurance in reblog_key_freq_pairs[:N]]

    reblog_key_clusters = []

    for reblog_key, occurance in reblog_key_freq_pairs:
        if len(reblog_key_clusters) >= N:
            break
        
        if (occurance > minsize) and occurance < maxsize:
            reblog_key_clusters.append(reblog_key)

    print "\nWe'll actually only be working with:"
    print reblog_key_clusters
    node_sizes = []
    
    for key in reblog_key_clusters:
        # Get all of the objects (key relations) for that given reblog_key
        key_relations = s.query(ReblogRelations).filter_by(reblog_key=key).all()
        print "Holy crap! we've got %s key relations to work with" % len(key_relations)
        print "\n\n"
        print key_relations
        print "\n\n"
        
        # Iterate through the relations and add them to our graph
        for relation in key_relations:
            child = extractBlogName(relation.reblogger)
            parent = extractBlogName(relation.poster)
            num_reblogs = getNumReblogs(relation.reblogger, key_relations)
            
            g.add_edge(child, parent) #child, parent
            g.node[child]['size'] = 500 + (num_reblogs * 500)
            g.node[parent]['size'] = 500 + (getNumReblogs(relation.poster, key_relations) * 600)
            
            
            
            
            if not g.node[child].has_key('style'):
                g.node[child]['style'] = 'child'
                
            g.node[parent]['style'] = 'parent'
                

    
        # include the reblog key in the description - so can identify
        #g.node[child]['desc'] = key_relations[0].reblog_key
    
       
    
    """ Drawing Graphs """
    
    print "\n\nEdges:" 
    for edge in g.edges():
        print edge
        
    print "\n\nNodes:"
    print g.nodes()        
        
    print "iterating through nodes:"
    for node in g.nodes():
        #print "node: %s" % node
        #print "gnode: %s" % g.node[node]
        #size = g.node[node]['size']
        size = 500
        
        if node == "coeurelectrique":
            print g.node[node]
            print node
        
        # add all of their children's sizes to it
        if g.node[node]['style'] == 'parent':        
            for edge in g.edges():
                child = edge[0]
                parent = edge[1]
                
                if parent == node:
                    print "%s gets %s from %s" % (parent, g.node[child]['size'], child)
                    size += g.node[child]['size']

        if size == 0:
            size = 600
        
        print "%s is now size %s" % (node, size)
        node_sizes.append(size)
        
        
    
    print "\nconfiguring graph parameters"
    pos=nx.spring_layout(g) #spring_layout
    
    print "positions: %s" % pos
    print "sizes: %s" % node_sizes
    
    length = g.number_of_edges()
    #colors=range(length)
    
    x = plt.figure(1)
    ax = x.add_subplot(111)
    #nx.draw_networkx(g, pos, node_color='#A0CBE2', edge_color=colors, node_size=node_sizes, width=widths, edge_cmap=plt.cm.Blues, with_labels=True)

    #y = plt.figure(2)
    print "drawing networkx"
    nx.draw_networkx(g, pos, node_color='#A0CBE2', node_size=node_sizes, \
    width=4, edge_cmap=plt.cm.Blues, with_labels=True)
    # edge_color=colors

    print "drawing/showing graph"
    plt.draw()
    plt.show()
    
    print "done!"
    
    
    
    #s.query(ReblogRelations).group_by(ReblogRelations.reblog_key).limit(10).all()



def getTopNMostCommentedPosts(s, N):
    """ Returns the N most commented posts """
    notes = s.query(Post).order_by("num_notes").all()
    notes.reverse()
    
    print "\n\nTop %s most commented posts:" % N
    print notes[:N]
    
    return notes[:N]


def getTopNMostRebloggedPosts(s, N):
    """ Returns the N most reblogged posts """
    reblogs = s.query(Post).order_by("num_reblogs").all()
    reblogs.reverse()
    
    print "\n\nTop %s most reblogged posts:" % N
    print reblogs[:N]
    
    return reblogs[:N]


def getTopNMostPopulatedBlogs(s, N):
    """ Gets the N blogs with the highest # of posts """
    blogs = s.query(Blog).all()
    top_blog_posts = []
    for blog in blogs:
        num_posts = len(blog.posts)
        if len(top_blog_posts) < N:
            top_blog_posts.append((blog.url, num_posts))
        else:
            for url,num in top_blog_posts:
                if num_posts > num:
                    top_blog_posts.remove((url, num))
                    top_blog_posts.append((blog.url, num_posts))
                    break
        
    
    print "\n\nTop %s blogs with most # of posts:" % N
    print top_blog_posts
    
    return top_blog_posts


if __name__ == "__main__":

    engine = create_engine('sqlite:///Database.db', echo=False) # Link to file
    Session = sessionmaker(bind=engine)
    s = Session()
    
    N = 2
    minsize = 5
    maxsize = 15
    visualizeGraph(s, minsize, maxsize)
    
    
    N = 5
    getTopNMostCommentedPosts(s, N)
    getTopNMostRebloggedPosts(s, N)
    getTopNMostPopulatedBlogs(s, N)






