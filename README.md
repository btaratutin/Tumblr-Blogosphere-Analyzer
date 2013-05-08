Tumblr-Blogosphere-Analyzer
===========================

This is a project I worked on in 2010 with a couple friends, in an attempt to crawl the Tumblr Blogosphere and analyze the relationships between the bloggers and rebloggers. 

This is a first-working-prototype that we built to see how big of a challenge it was and to better understand how to move forawrd. As such, there are definitely a lot of things I would change about the code - e.g. parallelizing it for use with cloud computing, using a more powerful database (like MySQL or Postgres), and generally adding little bits to streamline and simplify. But that's why I think it makes such a powerful tool at a code review - because we'll be able to talk about all those potential improvements.

Some of the things we built:
 * A general & scalable web crawler ("centipede.py") - manages scraper threads and saves results to DB
 * Class structures for Blog, Post, and ReblogRelations - that comprise the foundations of our project
 * Scripts that parse out Notes, Links, and other Blogs from any given blog post/page
 * Tools for cleaning up URL Links, visualizing the data, etc.
