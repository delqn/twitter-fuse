# FUSE Twitter client

## What it does

This software mounts twitter into a local directory.  A very subset of the twitter API is exposed via a file system in user space.   An authenticated twitter user's friends and their tweets appear listed in directories.  The root of this filesystem is a mountpoint specified as an input parameter of the executable.  The software assumes the existence of an app entity registered with twitter and the availability of its key and secret in the configuration file.


## Available Twitter data
Once the filesystem is mounted and a twitter user authenticated the following basic twitter data sets are available scoped to the provided credentials:
  - friends/followees:  `ls ./<mountpoint>`
  - friend's limited list of tweets: `ls ./<mountpoint>/<friend>`
  - contents of a given tweet: `cat ./<mountpount>/<friend>/<tweet_id>`


## Motivation
This is less of an effort to create yet another twitter client.  This is purely academic exploration of what's possible when the unix filesystem is thought of as the most common API to the digitized / computable world.  We start with the assumption that [the open/read/write/close system calls](https://www.kernel.org/doc/Documentation/filesystems/vfs.txt) of the modern UNIXes form an API language that is fairly simple, very well documented and most importantly available to and implemented by all computer languages, software packages and even small everyday tools.
The idea to represent a world living outside the hardware of our personal computer as a file system is hardly a novel idea.  Many recent projects expose various data streams as files but the idea seems to have been solidified and perhaps first widely adopted in the Plan9 system.

## What's possible
The files in a directory at very first glance is a list.  This implies that anything that is a reasonably long list could be represented is the contents of a directory.  For each item we have multiple dates at our disposal, various mode bits, tags etc.
A bit more complex view of the file system is the notion of a tree.  Perhaps anything machine readable that is in the form of parent-children-grandchildren could be represented as a file system.
Even more interesting is the representation of a graph.  Exposing a DAG as an FS seems possible within reason.

## Where is this going
As a thought experiment, this is attempting to answer a few interesting questions:
    - What are the limits of representing cyclic graphs as file systems
    - Is there an intuitive solution to the challenges of representing practically infinitely long lists (such as your twitter feed)
        - Could the idea of RESTful APIs' paging be somehow implemented in a file system


## Practical applications
Theoretically any application has the basic ability to open/read/close files.  This means that any executable would have access to the world abstracted by a file system.  For instance, a twitter feed exposed as a file system would allow us to:
    - read tweets with any text editor - vim, emacs, acme, eclipse
    - analyze content with powerful UNIX tools like cat, grep, sed, awk, perl, wc etc.
    - access a social stream with sophisticated tools like Excel, Matlab, Mathematica
    - use any scripting language to manipulate the data abstracted
