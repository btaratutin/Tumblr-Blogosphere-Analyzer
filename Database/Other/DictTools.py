# -*- coding: utf-8 -*-
"""
Created on Sun Jun 26 16:18:48 2011

@author: btaratutin
"""

def convertToHistogram(d):
    """ converts a {'key':[list]} dictionary to a {'key':freq} dict """
    d2 = {}
    
    for key, val in d.items():
        d2[key] = len(val)
        
    return d2    
    
    
from operator import itemgetter
def sortDict(d, key=0, reverse=False):
    """ Returns a sorted version of a dictionary (list of (key,val) pairs)
    
    Args:       d:      dictionary to be sorted
                key:    whether to sort by first (0) or second (1) tuple val
                reverse:whether to reverse the sort of the results (desc.)
    Returns:    sorted: a sorted list of tuple pairs (key, val) from the dict.
    """
    # Key: a function of one argument that is used to extract a comparison key 
    #      from each list element (ie. key=str.lower)
    # Itemgetter: returns a <callable object> 
    # Alt: key=lambda x: x[key]     # 10x slower, but more elegant (no imports)
    return sorted(d.iteritems(), key=itemgetter(key), reverse=reverse) 
    
    
def _sortDictGetValues(d, reverse=False):
    """ Returns a sorted version of a dictionary
    
    Args:       d: dictionary to be sorted
    Returns:    a list of the values (no keys), in ascending order
    """
    items = d.items()
    items.sort(reverse=reverse)
    return [val for key,val in items]
    
    
def sortDictRetLists(d):   
    """ Sorts dictionary d and returns two lists - the keys, and the vals 
    Returns:
        tuple of (key arr, value_arr) """
    keys = [key for key in sorted(d, key=d.get, reverse=True)]
    vals = [d[key] for key in sorted(d, key=d.get, reverse=True)]
    return (keys, vals)
    
def getTopN(d, N=10):
    """ Gets the top N dictionary values (assuming dict has int values) """
    (keys, vals) = sortDictRetLists(d)
    return [(key, d[key]) for key in keys[:N]]