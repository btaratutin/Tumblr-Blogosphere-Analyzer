# -*- coding: utf-8 -*-
"""
Created on Sat Jul 16 11:03:08 2011

@author: btaratutin
"""

#one-to-many
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
Base = declarative_base()

class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    children = relationship("Child", backref="parent")

class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('parent.id'))

"""
#many-to-one
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey('child.id'))
    child = relationship("Child", backref="parents")

class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True


#one-to-one
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey('child.id'))
    child = relationship("Child", backref=backref("parent", uselist=False))

class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True
"""

def createDB(dbname="Database.db"):
    print "Initializing Database\n"
    
    engine = create_engine('sqlite:///%s' % dbname, echo=False) # Link to file
    Base.metadata.create_all(engine)    # Generate data tables
    
    print "Success! Initialized %s" % dbname
    


if __name__ == "__main__":
    createDB("testdb.db")